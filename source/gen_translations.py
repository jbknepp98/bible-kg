"""Load Bible translations and their footnotes.

  migrations/06_translations.sql  (committed: public-domain and metadata only)
      translation table; verse_text gains status / import_note; BSB text; BSB footnotes in note; verse_citation
      (the BSB's "Cited in ..." footnotes as Old Testament -> New Testament verse links); views for Connect;
      drops the old trial table esv_text.
  migrations/91_licensed_translations.sql  (git-ignored: copyrighted text, never commit or publish)
      ESV text (esv_import.py) and NET text + NET footnotes.

Verses use the project's KJV numbering. A source verse with no counterpart (e.g. 3 John 15) is appended to the
previous verse; a verse a translation leaves out of its main text is stored with empty text and status 'not in text'.
Runs after 05_events.sql (and again after 03_text_places.sql, which rebuilds verse_text).

Usage: python3 gen_translations.py <theographic/json> <bsb usfm dir> <net usfm dir> <esv sqlite.sql>
"""
import collections, glob, json, os, re, sys
import esv_import
import cur_esv_patches as EP

THEO, BSB_DIR, NET_DIR, ESV_DUMP = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'migrations', '06_translations.sql')
LICENSED = os.path.join(HERE, '..', 'migrations', '91_licensed_translations.sql')

TRANSLATIONS = [
 # code, name, edition, licence, attribution, source
 ('KJV', 'King James Version', '1769 Oxford standard text', 'Public domain', 'King James Version (public domain).',
  'Theographic Bible Metadata'),
 ('ESV', 'English Standard Version', EP.EDITION, 'Copyright Crossway; used by permission', EP.ATTRIBUTION,
  'Unofficial SQLite copy (github.com/BIBLE-Study/SQLite-Databases), checked against esv.org and patched'),
 ('BSB', 'Berean Standard Bible', 'ebible.org engbsb (2026-10-20)', 'Public domain',
  'The Holy Bible, Berean Standard Bible, BSB is produced in cooperation with Bible Hub, Discovery Bible, '
  'OpenBible.com, and the Berean Bible Translation Committee. This text of God\'s Word has been dedicated to the '
  'public domain.', 'ebible.org engbsb USFM'),
 ('NET', 'New English Translation', 'ebible.org engnet (text with minimal notes)', 'Copyright Biblical Studies Press; used by permission',
  'Scripture quoted by permission. Quotations designated (NET) are from the NET Bible® copyright ©1996, 2019 by '
  'Biblical Studies Press, L.L.C. http://netbible.com All rights reserved.', 'ebible.org engnet USFM'),
]

USFM_BOOKS = dict(zip(
 'GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL '
 'AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB '
 'JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split(),
 'Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam '
 'Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil '
 'Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev'.split()))
SKIP_LINES = {'id', 'ide', 'h', 'toc1', 'toc2', 'toc3', 'mt', 'mt1', 'mt2', 'mt3', 'ms', 'ms1', 'ms2', 'mr', 's', 's1', 's2',
              's3', 'r', 'd', 'qa', 'sp', 'rem', 'cl'}
# Verse numbering that differs from the KJV numbering used here: source verse -> our verse (None = drop), and our
# verses whose text a translation counts as part of the previous verse.
VERSE_MAP = {'NET': {'2Cor.13.13': '2Cor.13.14', '2Cor.13.14': None}}
MERGED_INTO_PREVIOUS = {'NET': {'2Cor.13.13': 'The NET counts this text as part of 13:12 (different verse numbering).'}}
BOOK_NAMES = {b['fields']['bookName']: b['fields']['osisName'] for b in json.load(open(f'{THEO}/books.json'))}
OUR = [v['fields']['osisRef'] for v in sorted(json.load(open(f'{THEO}/verses.json')), key=lambda v: v['fields']['verseID'])]
OUR_SET = set(OUR)

def clean_inline(s):
    s = re.sub(r'\\w ([^|\\]*?)(\|[^\\]*)?\\w\*', r'\1', s)          # \w word|strong="..."\w*
    s = re.sub(r'\\\+?[a-z]+\d*\*?', ' ', s)                          # any remaining character marker
    return s

def parse_usfm(folder):
    """-> (texts {verse_id: text}, notes [(verse_id, seq, anchor, label, text)])"""
    texts, notes = collections.OrderedDict(), []
    for path in sorted(glob.glob(f'{folder}/*.usfm')):
        src = open(path, encoding='utf-8').read()
        m = re.search(r'^\\id (\w+)', src, re.M)
        if not m or m[1] not in USFM_BOOKS: continue
        book, chap, vid, pending = USFM_BOOKS[m[1]], None, None, []
        for line in src.split('\n'):
            mk = re.match(r'\\(\w+)', line)
            tag = mk[1] if mk else None
            if tag == 'd':                     # psalm title: its footnotes go to verse 1, labelled as such
                for fm in re.finditer(r'\\f .*?\\f\*', line):
                    pre = re.findall(r"[\w’']+", clean_inline(line[:fm.start()]))
                    pending.append((pre[-1] if pre else None, fm[0]))
                continue
            if tag in SKIP_LINES: continue
            if tag == 'c': chap = int(line.split()[1]); vid = None; continue
            body = line[mk.end():] if mk and tag not in ('v',) else line
            # walk the line: verse markers start verses, footnotes are cut out and recorded
            for part in re.split(r'(\\v \d+\s|\\f .*?\\f\*)', body):
                if not part: continue
                if part.startswith('\\v '):
                    vid = f'{book}.{chap}.{int(part.split()[1])}'
                    texts.setdefault(vid, '')
                    for anchor, fn in pending:
                        ft = re.sub(r'\\fr [^\\]*', '', fn[3:-3])
                        ft = re.sub(r'\s+', ' ', clean_inline(ft).replace('+', '', 1)).strip()
                        notes.append((vid, sum(1 for n in notes if n[0] == vid) + 1, anchor, 'Psalm title', ft))
                    pending = []
                elif part.startswith('\\f '):
                    if vid is None: continue
                    label = re.search(r'\\fl (.*?)(?=\\f[a-z]|\\f\*)', part)
                    ft = re.sub(r'\\fr [^\\]*', '', part[3:-3]); ft = re.sub(r'\\fl [^\\]*', '', ft)
                    ft = re.sub(r'\s+', ' ', clean_inline(ft).replace('+', '', 1)).strip()
                    words = re.findall(r"[\w’']+", clean_inline(texts[vid]))
                    notes.append((vid, sum(1 for n in notes if n[0] == vid) + 1, words[-1] if words else None,
                                  label[1].strip() if label else None, ft))
                elif vid is not None:
                    texts[vid] += ' ' + part
    out = collections.OrderedDict()
    for vid, raw in texts.items():
        t = re.sub(r'\s+', ' ', clean_inline(raw)).strip()
        t = re.sub(r'\s+([,.;:!?’”])', r'\1', t)
        out[vid] = t
    return out, notes

def remap(code, vid):
    m = VERSE_MAP.get(code, {})
    return m[vid] if vid in m else vid

def align(code, texts):
    """Map a translation onto our verse ids -> {verse_id: (text, status, note)}"""
    res, prev = {}, None
    for src_vid, t in texts.items():
        vid = remap(code, src_vid)
        if vid is None: continue
        if vid in OUR_SET:
            res[vid] = [t, 'as imported', None]; prev = vid
        else:                                      # numbering difference: keep the text with the previous verse
            res[prev][0] += ' ' + t; res[prev][1] = 'patched'
            b, c, v = vid.split('.')
            res[prev][2] = f'Includes {code} {c}:{v}, which the KJV numbering counts as part of this verse.'
    for vid, why in MERGED_INTO_PREVIOUS.get(code, {}).items():
        res[vid] = ['', 'merged into previous', why]
    for vid in OUR:
        if vid not in res or not res[vid][0]:
            if vid in res and res[vid][1] == 'merged into previous': continue
            res[vid] = ['', 'not in text', f'Not in the {code} main text (verse placed in a footnote or omitted).']
    return {k: tuple(v) for k, v in res.items()}

def kind_of(text, label):
    t = text.strip()
    if t == '[[EMPTY]]': return 'verse omitted'
    if t.startswith('Cited in') or t.startswith('Cited from'): return 'citation'
    if re.match(r'(Or|Or perhaps|Possibly)\b', t): return 'alternative rendering'
    if re.match(r'(Hebrew|Greek|Aramaic|Literally|Lit\.)\b', t): return 'literal meaning'
    if re.search(r'\b(manuscripts?|MT|LXX|SP|DSS|Septuagint|Syriac|Vulgate|Targum|Masoretic|Dead Sea|BYZ|TR|NE|WH|SBL|NA|ECM)\b', t):
        return 'manuscript variant'          # Greek NT notes cite editions: BYZ, TR, NE, WH, SBL
    if ONLY_REFS.fullmatch(t): return 'citation'   # New Testament note giving the Old Testament source of a quotation
    if re.search(r'\b(cubits?|shekels?|talents?|ephahs?|homers?|minas?|denarii|denarius|approximately|kilograms?|pounds|liters?|gallons?|miles|meters?|feet)\b', t, re.I): return 'measurement'
    if label and 'translator' in label.lower(): return 'translator note'
    return 'explanation'

REF = re.compile(r'((?:[1-3] )?[A-Z][a-z]+(?: of [A-Z][a-z]+)?) (\d+):(\d+)')
ONLY_REFS = re.compile(r'(?:(?:[1-3] )?[A-Z][a-z]+(?: of [A-Z][a-z]+)? \d+:\d+(?:[–-]\d+)?(?:, \d+(?:[–-]\d+)?)*'
                       r'(?: \(see also [^)]*\))?[;,]? ?(?:and )?)+\.?')
NT_BOOKS = set('Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas '
               '1Pet 2Pet 1John 2John 3John Jude Rev'.split())
def citations(notes):
    """Old Testament verse -> New Testament verse that quotes it, from both kinds of BSB note:
    'Cited in Acts 3:25' (anywhere in the note) on the Old Testament verse, and 'Exodus 21:17; Leviticus 20:9' on the New Testament verse."""
    out = []
    for vid, seq, anchor, label, text in notes:
        if vid.split('.')[0] in NT_BOOKS and ONLY_REFS.fullmatch(text.strip()):
            book = None
            for m in re.finditer(r'((?:[1-3] )?[A-Z][a-z]+(?: of [A-Z][a-z]+)?)?\s*(\d+):(\d+)', text):
                if m[1] and m[1] in BOOK_NAMES: book = BOOK_NAMES[m[1]]
                src = f'{book}.{m[2]}.{m[3]}' if book else None
                if src in OUR_SET and src.split('.')[0] not in NT_BOOKS: out.append((src, vid))
            continue
        # 'Cited in ...' may also close a longer note ('...; cited in Matthew 1:23.'). Read refs up to a ';' that is not
        # followed by another reference, so '; see also ...' cross-references are left out.
        cited = re.search(r'\b[Cc]ited in (.*?)(?:;(?!\s*(?:[1-3] )?[A-Z][a-z]+ \d)|$)', text)
        if not cited: continue
        book = None
        for m in re.finditer(r'((?:[1-3] )?[A-Z][a-z]+(?: of [A-Z][a-z]+)?)?\s*(\d+):(\d+)', cited[1]):
            if m[1] and m[1] in BOOK_NAMES: book = BOOK_NAMES[m[1]]
            if not book: continue
            to = f'{book}.{m[2]}.{m[3]}'
            if to in OUR_SET and to != vid: out.append((vid, to))
    return list(dict.fromkeys(out))

q = lambda v: 'NULL' if v is None else str(v) if isinstance(v, int) else "'" + str(v).replace("'", "''") + "'"
def note_rows(code, notes):
    rows = []
    for vid, seq, anchor, label, text in notes:
        vid = remap(code, vid)
        if vid is None or vid not in OUR_SET: continue
        k = kind_of(text, label)
        nid = f"{code}-{vid.replace('.', '-')}-{seq}"
        short = re.sub(r'\s*\([^)]*\)', '', text).strip()   # display names never carry brackets; Text keeps them
        disp = f"{k[0].upper() + k[1:]}: {short if len(short) <= 70 else short[:67].rsplit(' ', 1)[0] + '...'}"
        rows.append(f"({q(nid)}, {q(code)}, {q(vid)}, {seq}, {q(anchor)}, {q(label)}, {q(k)}, {q(text)}, {q(disp)})")
    return rows

def text_rows(code, aligned):
    tr = {t[0]: t for t in TRANSLATIONS}[code]
    # verse_text has short licence/attribution columns (40/120 chars); the full notices live once in translation
    lic = 'Public domain' if tr[3] == 'Public domain' else 'Used by permission'
    att = f'{tr[1]} ({code}); full notice in bible.translation'
    return [f"({q(v)}, {q(code)}, {q(t)}, {q(lic)}, {q(att)}, {q(s)}, {q(n)})" for v, (t, s, n) in aligned.items()]

# ---------------------------------------------------------------- read and align
bsb_text, bsb_notes = parse_usfm(BSB_DIR)
net_text, net_notes = parse_usfm(NET_DIR)
bsb, net = align('BSB', bsb_text), align('NET', net_text)
esv = {v: (t, s, n) for v, t, s, n in esv_import.load_esv(ESV_DUMP, THEO)}
cites = citations(bsb_notes)
for code, a in (('BSB', bsb), ('NET', net), ('ESV', esv)):
    assert set(a) == OUR_SET, code
    print(code, len(a), dict(collections.Counter(s for _, s, _ in a.values())))
print('BSB notes', len(bsb_notes), dict(collections.Counter(kind_of(t, l) for *_, l, t in bsb_notes)))
print('NET notes', len(net_notes), dict(collections.Counter(kind_of(t, l) for *_, l, t in net_notes)))
print('BSB citations (Cited in -> verse links)', len(cites))

COLS = 'verse_id, translation, text, license, attribution, status, import_note'
NOTE_COLS = 'note_id, translation, verse_id, seq, anchor, label, kind, text, display_name'
with open(PUBLIC, 'w', encoding='utf-8') as f:
    f.write('-- Translations and footnotes, public-domain part (generated by source/gen_translations.py)\n')
    f.write('SET search_path TO bible;\nBEGIN;\nDROP TABLE IF EXISTS esv_text CASCADE;\n')
    f.write('DROP VIEW IF EXISTS v_atlas_verse_translation, v_atlas_note, v_atlas_verse_citation;\n')
    f.write('DROP TABLE IF EXISTS verse_citation, note, translation CASCADE;\n')
    f.write('''CREATE TABLE translation (code varchar(8) PRIMARY KEY, name varchar(80) NOT NULL, edition varchar(120) NOT NULL,
  license varchar(120) NOT NULL, attribution text NOT NULL, source text NOT NULL);
ALTER TABLE verse_text ADD COLUMN IF NOT EXISTS status varchar(20) NOT NULL DEFAULT 'as imported';
ALTER TABLE verse_text ADD COLUMN IF NOT EXISTS import_note text;
CREATE TABLE note (note_id varchar(40) PRIMARY KEY, translation varchar(8) NOT NULL REFERENCES translation,
  verse_id varchar(16) NOT NULL REFERENCES verse, seq integer NOT NULL, anchor varchar(80), label varchar(80),
  kind varchar(30) NOT NULL, text text NOT NULL, display_name varchar(200) NOT NULL);
CREATE TABLE verse_citation (from_verse_id varchar(16) REFERENCES verse, to_verse_id varchar(16) REFERENCES verse,
  source varchar(20) NOT NULL, PRIMARY KEY (from_verse_id, to_verse_id));
''')
    f.write('INSERT INTO translation VALUES\n' + ',\n'.join('(' + ', '.join(q(x) for x in t) + ')' for t in TRANSLATIONS) + ';\n')
    f.write("UPDATE verse_text SET status = 'as imported', import_note = NULL WHERE translation = 'KJV';\n")
    f.write("DELETE FROM verse_text WHERE translation = 'BSB';\n")
    f.write(f'INSERT INTO verse_text ({COLS}) VALUES\n' + ',\n'.join(text_rows('BSB', bsb)) + ';\n')
    f.write(f'INSERT INTO note ({NOTE_COLS}) VALUES\n' + ',\n'.join(note_rows('BSB', bsb_notes)) + ';\n')
    f.write('INSERT INTO verse_citation VALUES\n' + ',\n'.join(f"({q(a)}, {q(b)}, 'BSB footnote')" for a, b in cites) + ';\n')
    f.write('''CREATE VIEW v_atlas_verse_translation AS
SELECT v.verse_id,
  COALESCE(MAX(t.text) FILTER (WHERE t.translation = 'ESV'), '') AS text_esv,
  COALESCE(MAX(t.import_note) FILTER (WHERE t.translation = 'ESV'), '') AS esv_note,
  COALESCE(MAX(t.text) FILTER (WHERE t.translation = 'BSB'), '') AS text_bsb,
  COALESCE(MAX(t.import_note) FILTER (WHERE t.translation = 'BSB'), '') AS bsb_note,
  COALESCE(MAX(t.text) FILTER (WHERE t.translation = 'NET'), '') AS text_net,
  COALESCE(MAX(t.import_note) FILTER (WHERE t.translation = 'NET'), '') AS net_note
FROM verse v LEFT JOIN verse_text t ON t.verse_id = v.verse_id GROUP BY v.verse_id;
CREATE VIEW v_atlas_note AS
SELECT n.note_id, n.translation, n.verse_id, v.book_id, n.seq, COALESCE(n.anchor, '') AS anchor, COALESCE(n.label, '') AS label,
       n.kind, n.text, n.display_name, v.chapter_number, v.verse_number
FROM note n JOIN verse v USING (verse_id);
CREATE VIEW v_atlas_verse_citation AS
SELECT c.*, v.book_id, v.chapter_number, v.verse_number, w.book_id AS to_book_id, w.chapter_number AS to_chapter_number,
       w.verse_number AS to_verse_number
FROM verse_citation c JOIN verse v ON v.verse_id = c.from_verse_id JOIN verse w ON w.verse_id = c.to_verse_id;
GRANT SELECT ON ALL TABLES IN SCHEMA bible TO timebase_reader;
COMMIT;
''')
with open(LICENSED, 'w', encoding='utf-8') as f:
    f.write('-- LICENSED TRANSLATION TEXT (ESV, NET): generated by source/gen_translations.py; git-ignored. Never commit or publish.\n')
    f.write("SET search_path TO bible;\nBEGIN;\nDELETE FROM note WHERE translation = 'NET';\nDELETE FROM verse_text WHERE translation IN ('ESV', 'NET');\n")
    f.write(f'INSERT INTO verse_text ({COLS}) VALUES\n' + ',\n'.join(text_rows('ESV', esv)) + ';\n')
    f.write(f'INSERT INTO verse_text ({COLS}) VALUES\n' + ',\n'.join(text_rows('NET', net)) + ';\n')
    f.write(f'INSERT INTO note ({NOTE_COLS}) VALUES\n' + ',\n'.join(note_rows('NET', net_notes)) + ';\n')
    f.write('COMMIT;\n')
print('wrote', PUBLIC, 'and', LICENSED)
