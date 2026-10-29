"""Replace scripture-reference display names ("Mary, Romans 16:6") using the rules in cur_names.py.

Reads people, role tables and relationships from initdb/02_data.sql, rewrites the display_name column of the
person COPY block in place, and writes an UPDATE script for a running database.

Usage: python3 gen_names.py [--check] [update.sql]
  --check   resolve and report only (writes names_preview.tsv); change nothing
"""
import collections, os, re, sys
import cur_names as CN
import cur_unnamed as CU

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'initdb', '02_data.sql')
check = '--check' in sys.argv
args = [a for a in sys.argv[1:] if a != '--check']
OUT_SQL = args[0] if args else os.path.join(HERE, 'names_update.sql')
REF_NAME = re.compile(r', (?:[1-3] )?[A-Z][a-z]+(?: [A-Z][a-z]+)* \d+:\d+(?:, no\. \d+)?$')
ORD = ['first', 'second', 'third', 'fourth', 'fifth']

lines = open(DATA, encoding='utf-8').read().split('\n')
def block(table):
    s = next(i for i, l in enumerate(lines) if l.startswith(f'COPY bible.{table} '))
    e = next(i for i in range(s + 1, len(lines)) if lines[i] == '\\.')
    cols = re.search(r'\((.*)\)', lines[s])[1].split(', ')
    return s, e, cols, [dict(zip(cols, lines[i].split('\t'))) for i in range(s + 1, e)]

ps, pe, pcols, people = block('person')
P = {p['person_id']: p for p in people}
king = {r['person_id']: r for r in block('king')[3]}
prophet = {r['person_id']: r for r in block('prophet')[3]}
priest = {r['person_id']: r for r in block('priest')[3]}
judge = {r['person_id']: r for r in block('judge')[3]}
descriptive = set(CU.EXISTING_DESCRIPTIVE)
nb = collections.defaultdict(lambda: collections.defaultdict(list))
for r in block('relationship')[3]:
    a, t, b = r['from_person_id'], r['relationship_type'], r['to_person_id']
    if t == 'Begot': nb[b]['parent'].append(a); nb[a]['child'].append(b)
    elif t == 'Married': nb[a]['spouse'].append(b); nb[b]['spouse'].append(a)
    elif t in ('SiblingOf', 'HalfSiblingOf'): nb[a]['sibling'].append(b); nb[b]['sibling'].append(a)

# an override key is a person_id or 'First reference|First name' (safer when ids are not known by heart)
by_ref = collections.defaultdict(list)
for p in people: by_ref[f"{p['first_reference']}|{p['first_name']}"].append(p['person_id'])
OVR = {}
for k, v in CN.OVERRIDES.items():
    if '|' in k:
        ids = by_ref.get(k, [])
        if len(ids) != 1: print(f'override key {k!r} matches {len(ids)} people: {ids}'); sys.exit(1)
        OVR[ids[0]] = v
    else:
        OVR[k] = v
CN.OVERRIDES = OVR
unknown = [k for k in CN.OVERRIDES if k not in P]
if unknown:
    print('OVERRIDES with unknown person_id:')
    for k in unknown:
        cands = [f"{q['person_id']} ({q['display_name']})" for q in people if q['first_name'].lower() == k.rsplit('_', 1)[0]]
        print(f'  {k}: {CN.OVERRIDES[k]!r}  candidates: {", ".join(cands[:6])}')
    sys.exit(1)

targets = [p['person_id'] for p in people if REF_NAME.search(p['display_name']) or p['person_id'] in CN.OVERRIDES]
used = collections.Counter(p['display_name'] for p in people if p['person_id'] not in targets)

def plain(pid):
    q = P[pid]
    return q['display_name'] if ',' not in q['display_name'] else q['first_name']

def word(kind, g):
    m = g == 'Male'
    return {'spouse': 'husband' if m else 'wife', 'child': 'father' if m else 'mother',
            'parent': 'son' if m else 'daughter', 'sibling': 'brother' if m else 'sister'}[kind]

def verse_role(ref):
    m = re.fullmatch(r'(.+) (\d+):(\d+)', ref or '')
    if not m: return None
    return next((r for c, lo, hi, r in CN.VERSE_ROLES if c == m[1] + ' ' + m[2] and lo <= int(m[3]) <= hi), None)

def candidates(pid):
    p = P[pid]; n = p['first_name']; ref = p['first_reference']
    if pid in CN.OVERRIDES: yield 'override', CN.OVERRIDES[pid]
    if (ref, n) in CN.RANKED: yield 'ranked', CN.RANKED[(ref, n)]
    g = CN.GENTILIC_BY_NAME.get((ref, n)) or CN.GENTILIC.get(ref)
    if g: yield 'gentilic', f'{n} {g}'
    if pid in king:
        yield 'role', f"{n}, king of {re.sub(r' [(].*[)]', '', king[pid]['kingdom'])}"
    if pid in prophet: yield 'role', f"{n} the {'prophetess' if p['gender'] == 'Female' else 'prophet'}"
    if pid in priest: yield 'role', f"{n} the {'high priest' if priest[pid]['is_high_priest'] == 't' else 'priest'}"
    if pid in judge: yield 'role', f'{n}, judge of Israel'
    for kind in ('spouse', 'child', 'parent', 'sibling'):
        rel = [o for o in nb[pid][kind] if o not in descriptive and o in P]
        for o in sorted(rel, key=lambda o: -int(P[o]['verse_count']))[:2]:
            yield 'family', f"{n}, {word(kind, p['gender'])} of {plain(o)}"
    role = verse_role(ref)
    if role: yield 'list role', f'{n}, {role}'
    if ref in CN.CLANS: yield 'clan', f'{n}, of the sons of {CN.CLANS[ref]}'

resolved, how, ordinal_groups = {}, collections.Counter(), collections.defaultdict(list)
for pid in sorted(targets, key=lambda k: (-int(P[k]['verse_count']), k)):
    cands = list(candidates(pid))
    pick = next(((h, c) for h, c in cands if not used[c]), None)
    if pick:
        resolved[pid] = pick[1]; how[pick[0]] += 1; used[pick[1]] += 1
    elif cands:
        ordinal_groups[cands[0][1]].append(pid)   # same best label, scripture gives nothing more
    else:
        how['UNRESOLVED'] += 1; resolved[pid] = None
for base, pids in ordinal_groups.items():
    # the person who already took the base label (if any) keeps it; the rest are numbered in verse order
    pids = sorted(pids, key=lambda k: (P[k]['first_reference'], k))
    for i, pid in enumerate(pids):
        name = f'{base}, {ORD[i + (1 if used[base] else 0)]}'
        assert not used[name], name
        resolved[pid] = name; used[name] += 1; how['ordinal'] += 1

print(f'{len(targets)} names to replace:', dict(how))
bad = [k for k, v in resolved.items() if v is None]
if bad:
    print('UNRESOLVED (need an override or verse role):')
    for k in bad: print(f"  {k:24} {P[k]['display_name']}")
allnames = [resolved.get(p['person_id'], p['display_name']) for p in people]
dups = [n for n, c in collections.Counter(allnames).items() if c > 1]
assert not dups, dups[:10]
if check or bad:
    with open(os.path.join(HERE, 'names_preview.tsv'), 'w', encoding='utf-8') as f:
        for k, v in sorted(resolved.items(), key=lambda kv: P[kv[0]]['display_name']):
            f.write(f"{k}\t{P[k]['display_name']}\t{v}\n")
    sys.exit(1 if bad else 0)

di = pcols.index('display_name')
for i in range(ps + 1, pe):
    row = lines[i].split('\t')
    if row[0] in resolved: row[di] = resolved[row[0]]; lines[i] = '\t'.join(row)
open(DATA, 'w', encoding='utf-8').write('\n'.join(lines))

q = lambda s: "'" + s.replace("'", "''") + "'"
with open(OUT_SQL, 'w', encoding='utf-8') as f:
    f.write('BEGIN;\nCREATE TEMP TABLE nm(person_id text PRIMARY KEY, display_name text) ON COMMIT DROP;\n')
    f.write('INSERT INTO nm VALUES\n' + ',\n'.join(f'({q(k)},{q(v)})' for k, v in resolved.items()) + ';\n')
    f.write("UPDATE bible.person p SET display_name = '~tmp~' || p.person_id FROM nm WHERE nm.person_id = p.person_id AND p.display_name <> nm.display_name;\n")
    f.write("UPDATE bible.person p SET display_name = nm.display_name FROM nm WHERE nm.person_id = p.person_id AND p.display_name LIKE '~tmp~%';\n")
    f.write('COMMIT;\n')
print(f'rewrote {DATA} and wrote {OUT_SQL}')
