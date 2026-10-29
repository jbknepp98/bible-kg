import json, re, sys, csv, io, collections
sys.path.insert(0, '/home/claude/work')
from resolve import R, BY
import cur_roles as CR, cur_rels as CRL, cur_people as CP

EXCLUDE = {  # spiritual beings and deities: not typed as Person (per scope)
 'god_1324','holy_spirit_7400','satan_2476','gabriel_1261','michael_2068','apollyon_2','lucifer_1832',
 'adrammelech_103','anammelech_254','ashtoreth_341','baal_573','baal-zebub_579','chemosh_931','dagon_969',
 'diana_1008','milcom_2084','molech_2104'}

link = re.compile(r'\[([^\]]*)\]\([^)]*\)')
def clean_easton(t):
    t = link.sub(r'\1', t or '').replace('\n', ' ')
    t = re.sub(r'\s+', ' ', t).strip().strip("'").strip()
    if len(re.sub(r'[^A-Za-z]', '', t)) < 25: return None
    out = ''
    for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z“"(])', t):
        if len(out) + len(sent) > 480 and out: break
        out = (out + ' ' + sent).strip()
    if len(out) > 600: out = out[:597].rsplit(' ', 1)[0] + '...'
    return out[0].upper() + out[1:]

def ylabel(y):
    if y is None: return None
    return f"{-y} BC" if y < 0 else f"AD {y}"

def to_int(v):
    try: return int(v)
    except: return None

BOOKNAME = {b['fields']['osisName']: b['fields']['bookName'] for b in json.load(open('/home/claude/theographic-bible-metadata/json/books.json'))}
def fmt_ref(r):
    if not r: return None
    b, c, v = r.split('.') if r.count('.') == 2 else (r, '', '')
    return f"{BOOKNAME.get(b, b)} {c}:{v}"

people = {k: v for k, v in BY.items() if k not in EXCLUDE}
ov = {R(k): v for k, v in CP.P.items()}

# ---------- relationships from source data ----------
rels = {}
def add(a, t, b, ref=None, src='Theographic', note=None):
    if not a or not b or a == b or a not in people or b not in people: return
    if t in SYM and a > b: a, b = b, a
    rels.setdefault((a, t, b), dict(ref=ref, src=src, note=note))
SYM = {'Married', 'SiblingOf', 'HalfSiblingOf'}
for k, o in people.items():
    for p in o['father'] + o['mother']: add(p, 'Begot', k)
    for c in o['children']: add(k, 'Begot', c)
    for s in o['siblings']: add(k, 'SiblingOf', s)
    for s in o['hsf'] + o['hsm']: add(k, 'HalfSiblingOf', s)
    for s in o['partners']: add(k, 'Married', s)
# a sibling pair that is also a half-sibling pair -> keep the more specific
for (a, t, b) in list(rels):
    if t == 'SiblingOf' and (a, 'HalfSiblingOf', b) in rels: del rels[(a, t, b)]

# ---------- curated narrative relationships ----------
for a, t, b, ref in CRL.RELS:
    if not a or not b: continue
    add(R(a), t, R(b), ref, 'Curated')

# ---------- king succession (programmatic, by kingdom order) ----------
kings = [(R(r[0]),) + tuple(r[1:]) for r in CR.KINGS]
for kingdom in ['Judah', 'Israel', 'Edom']:
    seq = [k for k in kings if k[1] == kingdom]
    for prev, cur in zip(seq, seq[1:]):
        add(cur[0], 'Succeeded', prev[0], None, 'Curated', f'Succession in {kingdom}')
uni = [R(x) for x in ['saul_2478', 'david_994', 'solomon_2762', 'rehoboam_2412']]
for prev, cur in zip(uni, uni[1:]): add(cur, 'Succeeded', prev, None, 'Curated', 'Succession in United Israel / Judah')
for a, b, note in [('shalmaneser_2529','tilgath-pilneser_2376','Succession in Assyria'),('ahasuerus_117','darius_978','Succession in Persia'),('artaxerxes_314','ahasuerus_117','Succession in Persia'),('esther_1343','vashti_2937','Queen of Persia')]:
    add(R(a), 'Succeeded', R(b), None, 'Curated', note)
add(R('jeroboam_872'), 'Opposed', R('rehoboam_2412'), '1 Kgs 12:16-20', 'Curated')

# ---------- person rows ----------
GROUPS_TRIBE = lambda gs: next((g for g in gs if g.startswith('Tribe of')), None)
name_count = collections.Counter(o['name'] for o in people.values())
names = {k: ov.get(k, {}).get('first', o['name']) for k, o in people.items()}

def generated_summary(o):
    he = 'man' if o['gender'] == 'Male' else 'woman'
    test = 'Old Testament' if (o['first'] or '').split('.')[0] in OT_BOOKS else 'New Testament'
    parts = [f"{o['name']} is a {he} named in the {test}" + (f", first mentioned at {fmt_ref(o['first'])}" if o['first'] else '') + '.']
    par = [names[p] for p in o['father'] + o['mother'] if p in names]
    if par: parts.append(f"{'Son' if o['gender']=='Male' else 'Daughter'} of {' and '.join(par)}.")
    sp = [names[p] for p in o['partners'] if p in names]
    if sp: parts.append(f"{'Husband' if o['gender']=='Male' else 'Wife'} of {', '.join(sp)}.")
    ch = [names[c] for c in o['children'] if c in names]
    if ch:
        lst = ', '.join(ch[:6]) + (f" and {len(ch)-6} others" if len(ch) > 6 else '')
        parts.append(f"{'Father' if o['gender']=='Male' else 'Mother'} of {lst}.")
    tribe = GROUPS_TRIBE(o['groups'])
    if tribe: parts.append(f"Of the {tribe.replace('Tribe of', 'tribe of')}.")
    if len(parts) == 1 and o['refs']:
        parts.append(f"Appears in {o['vc']} verse{'s' if o['vc']!=1 else ''} of Scripture.")
    return ' '.join(parts)

B = json.load(open('/home/claude/theographic-bible-metadata/json/books.json'))
OT_BOOKS = {b['fields']['osisName'] for b in B if b['fields']['testament'] == 'Old Testament'}

rows = []
for k, o in sorted(people.items()):
    c = ov.get(k, {})
    by = c.get('by', to_int(o['by'])); dy = c.get('dy', to_int(o['dy']))
    bp = c['bp'] if 'bp' in c else (o['bp'][0] if o['bp'] else None)
    dp = c['dp'] if 'dp' in c else (o['dp'][0] if o['dp'] else None)
    if 's' in c: summ, ssrc = c['s'], 'Curated'
    else:
        e = clean_easton(o['dict'])
        summ, ssrc = (e, "Easton's Bible Dictionary") if e else (generated_summary(o), 'Generated')
    first_book = (o['first'] or '').split('.')[0]
    testament = 'Old Testament' if first_book in OT_BOOKS else 'New Testament'
    rows.append(dict(
        person_id=k, first_name=c.get('first', o['name']), family_name=c.get('family', o['surname']),
        display_name=c.get('label'), also_known_as=c.get('aka', (o['also'] or '').replace(',', '; ') or None), gender=o['gender'],
        place_of_birth=bp, place_of_death=dp, year_of_birth=by, year_of_death=dy,
        year_of_birth_label=ylabel(by), year_of_death_label=ylabel(dy), manner_of_death=c.get('death'),
        testament=c.get('testament', testament), appears_in_both_testaments=len(o['test']) > 1,
        tribe=GROUPS_TRIBE(o['groups']), affiliations='; '.join(g for g in o['groups'] if not g.startswith('Tribe of')) or None,
        summary_of_life=summ, summary_source=ssrc, first_reference=fmt_ref(o['first']),
        verse_count=o['vc'], source_record_id=o['id']))

# unique display names
used = collections.Counter(r['display_name'] for r in rows if r['display_name'])
for r in rows:
    if r['display_name']: continue
    o = people[r['person_id']]
    if name_count[o['name']] == 1 and not used[r['first_name']]:
        r['display_name'] = r['first_name']
    else:
        par = [names[p] for p in o['father'] if p in names] or [names[p] for p in o['mother'] if p in names]
        cand = f"{r['first_name']}, {'son' if o['gender']=='Male' else 'daughter'} of {par[0]}" if par else None
        if not cand or used[cand]:
            cand = f"{r['first_name']}, {r['first_reference']}" if r['first_reference'] else f"{r['first_name']}, {r['person_id']}"
        r['display_name'] = cand
    used[r['display_name']] += 1
# names still shared (same name, same first verse) get ", no. N" in person_id order
# (gen_names.py later replaces every reference-style name with an epithet; see cur_names.py)
dupes = [n for n, c in collections.Counter(r['display_name'] for r in rows).items() if c > 1]
seq = collections.Counter()
for r in sorted(rows, key=lambda r: r['person_id']):
    if r['display_name'] in dupes:
        seq[r['display_name']] += 1
        r['display_name'] = f"{r['display_name']}, no. {seq[r['display_name']]}"

# ---------- role rows ----------
def roles(tbl, cols):
    out = []
    for row in getattr(CR, tbl):
        d = dict(zip(cols, row)); d['person_id'] = R(d.pop('key'))
        if d['person_id'] in people: out.append(d)
    seen = set(); res = []
    for d in out:
        if d['person_id'] in seen: continue
        seen.add(d['person_id']); res.append(d)
    return res
kings_t = roles('KINGS', ['key','kingdom','reign_start_year','reign_end_year','assessment','dynasty','royal_title'])
for d in kings_t:
    s, e = d['reign_start_year'], d['reign_end_year']
    d['reign_length_years'] = (e - s if e - s > 0 else 1) if s is not None and e is not None else None
    d['reign_start_label'], d['reign_end_label'] = ylabel(s), ylabel(e)
prophets_t = roles('PROPHETS', ['key','prophet_class','books_authored','ministry_start_year','ministry_end_year','audience','is_true_prophet'])
priests_t = roles('PRIESTS', ['key','priestly_order','is_high_priest','served_at','tenure_start_year','tenure_end_year'])
judges_t = roles('JUDGES', ['key','judge_order','tribe_of_origin','years_judged','oppressor','start_year'])
apostles_t = roles('APOSTLES', ['key','apostle_group','prior_occupation','calling_reference','death_tradition'])

ROLE_PRIORITY = ['King', 'Apostle', 'Prophet', 'Judge', 'Priest']
PRIMARY_OVERRIDE = {'aaron_1': 'Priest', 'eli_1072': 'Priest', 'zacharias_2971': 'Priest'}
role_sets = collections.defaultdict(set)
for name, tbl in [('King', kings_t), ('Prophet', prophets_t), ('Priest', priests_t), ('Judge', judges_t), ('Apostle', apostles_t)]:
    for d in tbl: role_sets[d['person_id']].add(name)
for r in rows:
    rs = role_sets.get(r['person_id'], set())
    r['roles'] = '; '.join(x for x in ROLE_PRIORITY if x in rs) or None
    r['primary_role'] = PRIMARY_OVERRIDE.get(r['person_id']) or next((x for x in ROLE_PRIORITY if x in rs), 'Person')
rel_rows = []
for i, ((a, t, b), m) in enumerate(sorted(rels.items()), 1):
    rel_rows.append(dict(relationship_id=i, from_person_id=a, relationship_type=t, to_person_id=b,
                         scripture_reference=m['ref'], source=m['src'], notes=m['note']))

json.dump(dict(person=rows, king=kings_t, prophet=prophets_t, priest=priests_t, judge=judges_t, apostle=apostles_t,
               relationship=rel_rows), open('/home/claude/work/final.json', 'w'), indent=1, default=str)
print('people', len(rows), 'rels', len(rel_rows), collections.Counter(r['relationship_type'] for r in rel_rows))
print('kings', len(kings_t), 'prophets', len(prophets_t), 'priests', len(priests_t), 'judges', len(judges_t), 'apostles', len(apostles_t))
print(collections.Counter(r['summary_source'] for r in rows))
