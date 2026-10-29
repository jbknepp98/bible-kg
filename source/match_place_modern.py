"""Derive modern names and countries for places -> source/place_modern.tsv (committed; read by gen_phase2_adjust.py).

  modern_name    regions: cur_place_modern.REGIONS. Other places: the best-scored modern identification in
                 OpenBible.info's Bible Geocoding Data (CC BY 4.0), accepted only when OpenBible's confidence is
                 >= 500 and the site lies within 15 km of the place's coordinates (or, for waters, mountains and
                 valleys, when the name has exactly one OpenBible candidate). Otherwise left empty, not guessed.
  modern_country the Natural Earth admin-0 country containing the place's coordinates (public domain), unless a
                 curated region gives the countries, then COUNTRY_CONVENTION applied ('Palestine' -> 'Israel').
                 Places in open water get none.

Usage: python3 match_place_modern.py <theographic/json dir> <openbible data dir> <ne_50m_admin_0_countries.geojson>
"""
import collections, json, math, os, re, sys
import cur_place_modern as CPM

THEO, OB, NE = sys.argv[1:4]
HERE = os.path.dirname(os.path.abspath(__file__))
WIDE = {'Water', 'Mountain', 'Valley'}
# Country convention (Jeff, 2026-10-29): every site west of the Jordan is 'Israel', including Jerusalem, the West Bank
# and Gaza, which Natural Earth labels 'Palestine'.
COUNTRY_CONVENTION = {'Palestine': 'Israel'}

def convention(countries):
    out = []
    for c in (countries or '').split('; '):
        c = COUNTRY_CONVENTION.get(c, c)
        if c and c not in out: out.append(c)
    return '; '.join(out) or None

def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))

base = lambda s: re.sub(r'\s+\d+$', '', re.sub(r'\s*\(.*\)$', '', s or '')).strip().lower()

# ---- countries: point in polygon over Natural Earth admin-0
countries = []
for f in json.load(open(NE))['features']:
    g = f['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for poly in polys:
        ring = poly[0]
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        countries.append((f['properties']['NAME'], (min(xs), min(ys), max(xs), max(ys)), poly))

def inside(ring, x, y):
    c, j = False, len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][:2]; xj, yj = ring[j][:2]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c

def country_at(lat, lon):
    for name, (x0, y0, x1, y1), poly in countries:
        if x0 <= lon <= x1 and y0 <= lat <= y1 and inside(poly[0], lon, lat) \
           and not any(inside(h, lon, lat) for h in poly[1:]):
            return name
    return None

# ---- OpenBible: best modern identification for each ancient place, indexed by base name
modern = {r['id']: r for r in (json.loads(l) for l in open(f'{OB}/modern.jsonl'))}
byname, ncand = collections.defaultdict(list), collections.Counter()
for a in (json.loads(l) for l in open(f'{OB}/ancient.jsonl')):
    ncand[base(a['friendly_id'])] += 1
    ma = a.get('modern_associations') or {}
    if not ma: continue
    mid, info = max(ma.items(), key=lambda kv: kv[1].get('score', 0))
    if mid not in modern or not modern[mid].get('lonlat'): continue
    lon, lat = map(float, modern[mid]['lonlat'].split(','))
    byname[base(a['friendly_id'])].append(dict(name=info['name'], score=info.get('score', 0), ll=(lat, lon), ob=a['friendly_id']))

rows, how = [], collections.Counter()
for p in (x['fields'] for x in json.load(open(f'{THEO}/places.json'))):
    pid, ft = p['placeLookup'], p.get('featureType') or 'Unknown'
    lat, lon = p.get('latitude'), p.get('longitude')
    ll = (float(lat), float(lon)) if lat and lon else None
    name, country, method = None, country_at(*ll) if ll else None, 'computed country'
    if pid in CPM.REGIONS:
        name, cc = CPM.REGIONS[pid]
        country, method = cc or country, 'curated region'
    elif ft != 'Region':
        ref = (float(p['openBibleLat']), float(p['openBibleLong'])) if p.get('openBibleLat') else ll
        names = {base(p.get(k)) for k in ('kjvName', 'esvName', 'displayTitle') if p.get(k)}
        cands = [c for n in names for c in byname.get(n, [])]
        if ref and cands:
            best = min(cands, key=lambda c: km(ref, c['ll']))
            d = km(ref, best['ll'])
            if best['score'] >= 500 and (d <= 15 or (ft in WIDE and ncand[base(best['ob'])] == 1)):
                name, method = best['name'], f"OpenBible (confidence {best['score']}, {d:.1f} km)"
    if name is None and country is None: continue
    how[method.split(' (')[0]] += 1
    rows.append((pid, name or '', convention(country) or '', method))

with open(os.path.join(HERE, 'place_modern.tsv'), 'w', encoding='utf-8') as f:
    f.write('place_id\tmodern_name\tmodern_country\tmethod\n')
    for r in sorted(rows): f.write('\t'.join(r) + '\n')
print(f'{len(rows)} places: {dict(how)}; with modern name {sum(1 for r in rows if r[1])}, with country {sum(1 for r in rows if r[2])}')
print('countries used:', collections.Counter(c for r in rows for c in r[2].split('; ') if c).most_common(25))
