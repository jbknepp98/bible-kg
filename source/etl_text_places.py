"""Phase 2 ETL: Books, Chapters, Verses (KJV text), Places and their links.
Reads Theographic JSON + the Phase 1 person table (final.json) and writes migrations/03_text_places.sql.
Usage: python3 -I etl_text_places.py <theographic_json_dir> <final.json> <out_sql>
"""
import json, ast, re, sys, collections

TDIR, FINAL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
L = lambda s: s if isinstance(s, list) else (ast.literal_eval(s) if s else [])
J = lambda n: json.load(open(f'{TDIR}/{n}.json'))
V, P, PL, B, C = J('verses'), J('people'), J('places'), J('books'), J('chapters')
persons = {r['person_id'] for r in json.load(open(FINAL))['person']}   # Phase 1 keys (excludes spiritual beings)
prec = {p['id']: p['fields']['personLookup'] for p in P}
plrec = {p['id']: p['fields']['placeLookup'] for p in PL}
bookrec = {b['id']: b['fields'] for b in B}

link = re.compile(r'\[([^\]]*)\]\([^)]*\)')
def clean(t):
    t = re.sub(r'\s+', ' ', link.sub(r'\1', t or '')).strip()
    if len(re.sub(r'[^A-Za-z]', '', t)) < 25: return None
    out = ''
    for s in re.split(r'(?<=[.!?])\s+(?=[A-Z“"(])', t):
        if len(out) + len(s) > 480 and out: break
        out = (out + ' ' + s).strip()
    return out[:600]

# ---------- curated book facts (66 rows) ----------
GENRE = {**{b: 'Law' for b in ['Exod','Lev','Num','Deut']}, 'Gen': 'Narrative',
 **{b: 'Narrative' for b in ['Josh','Judg','Ruth','1Sam','2Sam','1Kgs','2Kgs','1Chr','2Chr','Ezra','Neh','Esth','Acts']},
 **{b: 'Poetry' for b in ['Ps','Song','Lam']}, **{b: 'Wisdom' for b in ['Job','Prov','Eccl']},
 **{b: 'Prophecy' for b in ['Isa','Jer','Ezek','Hos','Joel','Amos','Obad','Jonah','Mic','Nah','Hab','Zeph','Hag','Zech','Mal']},
 'Dan': 'Apocalyptic', 'Rev': 'Apocalyptic', **{b: 'Gospel' for b in ['Matt','Mark','Luke','John']}}
STATED = {'Neh','Eccl','Song','Prov','Isa','Jer','Ezek','Dan','Hos','Joel','Amos','Obad','Jonah','Mic','Nah','Hab','Zeph','Hag','Zech','Mal',
          'Rom','1Cor','2Cor','Gal','Eph','Phil','Col','1Thess','2Thess','1Tim','2Tim','Titus','Phlm','Jas','1Pet','2Pet','Jude','Rev'}
def book_lang(osis, test):
    if test == 'New Testament': return 'Greek'
    return 'Hebrew and Aramaic' if osis in ('Dan', 'Ezra') else 'Hebrew'

pname = {}
for r in json.load(open(FINAL))['person']: pname[r['person_id']] = r['first_name']

books, book_writer = [], set()
for b in B:
    f = b['fields']; o = f['osisName']
    ws = [w.strip() for x in L(f.get('writers')) for w in x.split(',') if w.strip()]
    ws = list(dict.fromkeys(w for w in ws if w in persons))
    for w in ws: book_writer.add((o, w))
    conf = 'Unknown' if o == 'Heb' else ('Stated in text' if o in STATED else 'Traditional')
    books.append(dict(book_id=o, name=f['bookName'], short_name=f.get('shortName'), book_order=int(f['bookOrder']),
        testament=f['testament'], division=f.get('bookDiv'), genre=GENRE.get(o, 'Epistle'),
        original_language=book_lang(o, f['testament']), chapter_count=int(f['chapterCount']), verse_count=int(f['verseCount']),
        author_traditional=', '.join(pname.get(w, w) for w in ws) or None, authorship_confidence=conf,
        composition_year_start=None, composition_year_end=None, composition_date_label=None, dating_basis=None, summary=None,
        source='Theographic + curated genre/language/authorship confidence'))

chapters = []
for c in C:
    f = c['fields']; o = bookrec[L(f['book'])[0]]['osisName']
    chapters.append(dict(chapter_id=f['osisRef'], book_id=o, chapter_number=int(f['chapterNum']), verse_count=len(L(f.get('verses')))))

verses, verse_text, verse_person, verse_place = [], [], set(), set()
for v in V:
    f = v['fields']; bo = bookrec[L(f['book'])[0]]
    o, ch, vn = f['osisRef'].split('.')
    yr = int(f['yearNum']) if f.get('yearNum') not in (None, '') else None
    verses.append(dict(verse_id=f['osisRef'], verse_sort=int(f['verseID']), book_id=o, chapter_id=f'{o}.{ch}',
        chapter_number=int(ch), verse_number=int(vn), reference_label=f"{bo['bookName']} {ch}:{vn}",
        approx_year=yr, dating_basis='Theographic (Ussher-based)' if yr is not None else None))
    verse_text.append(dict(verse_id=f['osisRef'], translation='KJV', text=f.get('verseText'),
        license='Public Domain', attribution='King James Version via Theographic Bible Metadata'))
    for x in L(f.get('people')):
        if prec.get(x) in persons: verse_person.add((f['osisRef'], prec[x]))
    for x in L(f.get('places')):
        if x in plrec: verse_place.add((f['osisRef'], plrec[x]))

# ---------- places ----------
STATUS = {'VERIFIED': 'Verified', 'UNVERIFIED': 'Unverified', 'NOT_IDENTIFIABLE': 'Not identifiable'}
vref = {v['id']: (v['fields']['osisRef'], int(v['fields']['verseID'])) for v in V}
OTB = {b['osisName'] for b in bookrec.values() if b['testament'] == 'Old Testament'}
names = collections.Counter(p['fields']['displayTitle'] for p in PL)
def fnum(x):
    try: return float(x)
    except: return None
places, used = [], collections.Counter()
for p in PL:
    f = p['fields']; refs = sorted(vref[x] for x in L(f.get('verses')) if x in vref)
    tests = {('Old' if r[0].split('.')[0] in OTB else 'New') for r in refs}
    first = refs[0][0] if refs else None
    firstlbl = None
    if first:
        o, ch, vn = first.split('.'); firstlbl = f"{next(b['bookName'] for b in bookrec.values() if b['osisName']==o)} {ch}:{vn}"
    ft = f.get('featureType') or 'Unknown'
    dn = f['displayTitle']
    if names[dn] > 1:
        dn = f"{dn} ({ft.lower()}, {firstlbl})" if firstlbl else f"{dn} ({f['placeLookup']})"
    if used[dn]: dn = f"{dn} [{f['placeLookup']}]"
    used[dn] += 1
    summ = clean((L(f.get('dictText')) or [''])[0] if f.get('dictText') else '')
    places.append(dict(place_id=f['placeLookup'], name=f['displayTitle'], display_name=dn, kjv_name=f.get('kjvName'), esv_name=f.get('esvName'),
        also_known_as=(f.get('aliases') or '').replace(', ', '; ') or None, feature_type=ft, feature_sub_type=f.get('featureSubType'),
        latitude=fnum(f.get('latitude')) if fnum(f.get('longitude')) is not None else None,
        longitude=fnum(f.get('longitude')) if fnum(f.get('latitude')) is not None else None,
        coordinate_source='Theographic' if fnum(f.get('latitude')) is not None and fnum(f.get('longitude')) is not None else None,
        openbible_latitude=fnum(f.get('openBibleLat')), openbible_longitude=fnum(f.get('openBibleLong')),
        location_precision=f.get('precision') or 'Unknown', identification_status=STATUS.get(f.get('recogitoStatus'), 'Unknown'),
        modern_name=None, modern_country=None, notes=f.get('comment'),
        testament={'Old': 'Old Testament', 'New': 'New Testament'}.get(''.join(tests)) if len(tests) == 1 else ('Both' if tests else None),
        verse_count=int(f['verseCount']), first_reference=firstlbl,
        summary=summ, summary_source="Easton's Bible Dictionary" if summ else None))

place_rel = set()
for p in PL:
    f = p['fields']; me = f['placeLookup']
    for x in L(f.get('partOf')): place_rel.add((me, 'partOf', plrec[x]))
    for x in L(f.get('parts')): place_rel.add((plrec[x], 'partOf', me))
    for k in ('near', 'nearby'):
        for x in L(f.get(k)): place_rel.add(tuple(sorted((me, plrec[x]))[:1]) + ('near',) + tuple(sorted((me, plrec[x]))[1:]))
    for k in ('otherNames', 'canonicalPlace'):
        for x in L(f.get(k)): place_rel.add(tuple(sorted((me, plrec[x]))[:1]) + ('sameAs',) + tuple(sorted((me, plrec[x]))[1:]))
place_rel = {r for r in place_rel if r[0] != r[2]}

person_place = set()
for p in P:
    f = p['fields']; me = f['personLookup']
    if me not in persons: continue
    for x in L(f.get('birthPlace')): person_place.add((me, 'bornIn', plrec[x]))
    for x in L(f.get('deathPlace')): person_place.add((me, 'diedIn', plrec[x]))
for p in PL:
    for n in [s.strip() for s in (p['fields'].get('hasBeenHere') or '').split(',') if s.strip()]:
        if n in persons: person_place.add((n, 'visited', p['fields']['placeLookup']))

# ---------- SQL ----------
DDL = r"""
-- Phase 2 migration: Books, Chapters, Verses, Verse text, Places and links. Idempotent: drops and recreates Phase 2 objects only.
BEGIN;
SET search_path TO bible;
DROP VIEW IF EXISTS v_atlas_book, v_atlas_chapter, v_atlas_verse, v_atlas_verse_text, v_atlas_place,
  v_atlas_book_writer, v_atlas_verse_person, v_atlas_verse_place, v_atlas_place_relation, v_atlas_person_place CASCADE;
DROP TABLE IF EXISTS person_place, place_relation, verse_place, verse_person, verse_text, verse, chapter, book_writer, book, place CASCADE;

CREATE TABLE book (
  book_id varchar(8) PRIMARY KEY, name varchar(40) NOT NULL UNIQUE, short_name varchar(8), book_order integer NOT NULL UNIQUE,
  testament varchar(20) NOT NULL CHECK (testament IN ('Old Testament','New Testament')), division varchar(30) NOT NULL,
  genre varchar(20) NOT NULL, original_language varchar(30) NOT NULL, chapter_count integer NOT NULL, verse_count integer NOT NULL,
  author_traditional varchar(120), authorship_confidence varchar(20) NOT NULL CHECK (authorship_confidence IN ('Stated in text','Traditional','Unknown')),
  composition_year_start integer, composition_year_end integer, composition_date_label varchar(40), dating_basis varchar(60),
  summary text, source varchar(80) NOT NULL);
CREATE TABLE book_writer (book_id varchar(8) REFERENCES book, person_id varchar(64) REFERENCES person, PRIMARY KEY (book_id, person_id));
CREATE TABLE chapter (chapter_id varchar(16) PRIMARY KEY, book_id varchar(8) NOT NULL REFERENCES book, chapter_number integer NOT NULL,
  verse_count integer NOT NULL, UNIQUE (book_id, chapter_number));
CREATE TABLE verse (verse_id varchar(20) PRIMARY KEY, verse_sort integer NOT NULL UNIQUE, book_id varchar(8) NOT NULL REFERENCES book,
  chapter_id varchar(16) NOT NULL REFERENCES chapter, chapter_number integer NOT NULL, verse_number integer NOT NULL,
  reference_label varchar(40) NOT NULL, approx_year integer, dating_basis varchar(40));
CREATE TABLE verse_text (verse_id varchar(20) REFERENCES verse, translation varchar(10) NOT NULL, text text NOT NULL,
  license varchar(40) NOT NULL, attribution varchar(120) NOT NULL, PRIMARY KEY (verse_id, translation));
CREATE TABLE place (
  place_id varchar(64) PRIMARY KEY, name varchar(80) NOT NULL, display_name varchar(160) NOT NULL UNIQUE,
  kjv_name varchar(80), esv_name varchar(80), also_known_as varchar(200),
  feature_type varchar(20) NOT NULL, feature_sub_type varchar(20),
  latitude double precision, longitude double precision, coordinate_source varchar(20),
  openbible_latitude double precision, openbible_longitude double precision,
  location_precision varchar(30) NOT NULL, identification_status varchar(20) NOT NULL
    CHECK (identification_status IN ('Verified','Unverified','Not identifiable','Unknown')),
  modern_name varchar(80), modern_country varchar(80), notes text,
  testament varchar(20) CHECK (testament IN ('Old Testament','New Testament','Both')),
  verse_count integer NOT NULL, first_reference varchar(40), summary text, summary_source varchar(40));
CREATE TABLE verse_person (verse_id varchar(20) REFERENCES verse, person_id varchar(64) REFERENCES person, PRIMARY KEY (verse_id, person_id));
CREATE TABLE verse_place  (verse_id varchar(20) REFERENCES verse, place_id varchar(64) REFERENCES place, PRIMARY KEY (verse_id, place_id));
CREATE TABLE place_relation (from_place_id varchar(64) REFERENCES place, relation_type varchar(10) NOT NULL CHECK (relation_type IN ('partOf','near','sameAs')),
  to_place_id varchar(64) REFERENCES place, PRIMARY KEY (from_place_id, relation_type, to_place_id), CHECK (from_place_id <> to_place_id));
CREATE TABLE person_place (person_id varchar(64) REFERENCES person, relation_type varchar(10) NOT NULL CHECK (relation_type IN ('bornIn','diedIn','visited')),
  place_id varchar(64) REFERENCES place, PRIMARY KEY (person_id, relation_type, place_id));
CREATE INDEX ix_verse_chapter ON verse(chapter_id); CREATE INDEX ix_vp_person ON verse_person(person_id); CREATE INDEX ix_vpl_place ON verse_place(place_id);
"""
VIEWS = r"""
CREATE VIEW v_atlas_book AS SELECT * FROM book;
CREATE VIEW v_atlas_book_writer AS SELECT book_id, person_id FROM book_writer;
CREATE VIEW v_atlas_chapter AS SELECT c.*, b.name AS book_name FROM chapter c JOIN book b USING (book_id);
CREATE VIEW v_atlas_verse AS SELECT v.*, t.text AS text_kjv FROM verse v LEFT JOIN verse_text t ON t.verse_id = v.verse_id AND t.translation = 'KJV';
CREATE VIEW v_atlas_verse_text AS SELECT * FROM verse_text;
CREATE VIEW v_atlas_place AS SELECT * FROM place;
CREATE VIEW v_atlas_verse_person AS SELECT vp.verse_id, vp.person_id, v.book_id FROM verse_person vp JOIN verse v USING (verse_id);
CREATE VIEW v_atlas_verse_place  AS SELECT vp.verse_id, vp.place_id, v.book_id FROM verse_place vp JOIN verse v USING (verse_id);
CREATE VIEW v_atlas_place_relation AS SELECT * FROM place_relation;
CREATE VIEW v_atlas_person_place AS SELECT * FROM person_place;
GRANT SELECT ON ALL TABLES IN SCHEMA bible TO timebase_reader;
COMMIT;
"""
def esc(v):
    if v is None: return r'\N'
    if isinstance(v, bool): return 't' if v else 'f'
    return str(v).replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
def copy(t, cols, rows):
    out = [f"COPY bible.{t} ({', '.join(cols)}) FROM stdin;"]
    out += ['\t'.join(esc(r[c] if isinstance(r, dict) else r[i]) for i, c in enumerate(cols)) for r in rows]
    return '\n'.join(out) + '\n\\.\n'
parts = [DDL]
for t, rows in [('book', books), ('chapter', chapters), ('verse', verses), ('verse_text', verse_text), ('place', places)]:
    parts.append(copy(t, list(rows[0].keys()), rows))
parts.append(copy('book_writer', ['book_id', 'person_id'], sorted(book_writer)))
parts.append(copy('verse_person', ['verse_id', 'person_id'], sorted(verse_person)))
parts.append(copy('verse_place', ['verse_id', 'place_id'], sorted(verse_place)))
parts.append(copy('place_relation', ['from_place_id', 'relation_type', 'to_place_id'], sorted(place_rel)))
parts.append(copy('person_place', ['person_id', 'relation_type', 'place_id'], sorted(person_place)))
parts.append(VIEWS)
open(OUT, 'w').write('\n'.join(parts))
pr = collections.Counter(r[1] for r in place_rel); pp = collections.Counter(r[1] for r in person_place)
print(dict(books=len(books), book_writer=len(book_writer), chapters=len(chapters), verses=len(verses), verse_text=len(verse_text),
           places=len(places), verse_person=len(verse_person), verse_place=len(verse_place), place_relation=dict(pr), person_place=dict(pp)))
