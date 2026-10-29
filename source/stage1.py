import json,re,ast,collections
T='/home/claude/theographic-bible-metadata/json/'
P=json.load(open(T+'people.json'))
V=json.load(open(T+'verses.json'))
B=json.load(open(T+'books.json'))
PL=json.load(open(T+'places.json'))
PG=json.load(open(T+'peopleGroups.json'))
def L(s):
    if not s: return []
    return ast.literal_eval(s) if isinstance(s,str) else s
book={b['id']:b['fields'] for b in B}
verse={}
for v in V:
    f=v['fields']; bid=L(f['book'])[0]
    verse[v['id']]=(f['verseID'],f['osisRef'],book[bid]['testament'],book[bid]['bookName'])
place={p['id']:p['fields']['displayTitle'] for p in PL}
grp={}
for g in PG:
    for m in L(g['fields'].get('members')): grp.setdefault(m,[]).append(g['fields']['groupName'])
rec2look={p['id']:p['fields']['personLookup'] for p in P}
out=[]
for p in P:
    f=p['fields']
    vs=sorted([verse[x] for x in L(f.get('verses')) if x in verse])
    test=set(v[2] for v in vs)
    out.append(dict(id=p['id'],lookup=f['personLookup'],name=f['name'],display=f['displayTitle'],surname=f.get('surname'),
      also=f.get('alsoCalled'),gender=f['gender'],disamb=f.get('Disambiguation (temp)'),
      by=f.get('birthYear'),dy=f.get('deathYear'),bp=[place.get(x) for x in L(f.get('birthPlace'))],dp=[place.get(x) for x in L(f.get('deathPlace'))],
      groups=grp.get(p['id'],[]),dict=(L(f.get('dictText')) or [''])[0] if f.get('dictText') else '',
      vc=int(f['verseCount']),first=vs[0][1] if vs else None,firstbook=vs[0][3] if vs else None,refs=[v[1] for v in vs],
      test=sorted(test),father=[rec2look[x] for x in L(f.get('father')) if x in rec2look],mother=[rec2look[x] for x in L(f.get('mother')) if x in rec2look],
      partners=[rec2look[x] for x in L(f.get('partners')) if x in rec2look],children=[rec2look[x] for x in L(f.get('children')) if x in rec2look],
      siblings=[rec2look[x] for x in L(f.get('siblings')) if x in rec2look],hsf=[rec2look[x] for x in L(f.get('halfSiblingsSameFather')) if x in rec2look],
      hsm=[rec2look[x] for x in L(f.get('halfSiblingsSameMother')) if x in rec2look]))
json.dump(out,open('/home/claude/work/people_stage1.json','w'),indent=0)
with open('/home/claude/work/index.tsv','w') as fh:
    for o in sorted(out,key=lambda o:o['lookup']):
        fh.write(f"{o['lookup']}\t{o['display']}\t{o['disamb'] or ''}\t{o['vc']}\t{o['first']}\t{','.join(o['test'])}\t{(o['dict'] or '')[:90]}\n")
print(len(out), collections.Counter(tuple(o['test']) for o in out))
