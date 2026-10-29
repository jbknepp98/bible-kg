import json
P=json.load(open('/home/claude/work/people_stage1.json'))
BY={o['lookup']:o for o in P}
NAME={}
for o in P:
    for n in {o['name'].lower(),o['display'].lower()}|{a.strip().lower() for a in (o['also'] or '').split(',') if a.strip()}:
        NAME.setdefault(n,[]).append(o)
def R(key):
    """key: lookup id, 'Name', or 'Name@Book.C.V'"""
    if key in BY: return key
    if '@' in key:
        n,ref=key.split('@')
        c=[o for o in NAME.get(n.lower(),[]) if ref in o['refs']]
        if not c:  # chapter-level fallback
            ch=ref.rsplit('.',1)[0]+'.'
            c=[o for o in NAME.get(n.lower(),[]) if any(r.startswith(ch) for r in o['refs'])]
    else:
        c=NAME.get(key.lower(),[])
    if not c: raise KeyError('UNRESOLVED '+key)
    return max(c,key=lambda o:o['vc'])['lookup']
