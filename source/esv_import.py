"""Read the ESV text from the unofficial SQLite dump (as text; it is never executed) and apply cur_esv_patches.py.

Used by gen_translations.py. load_esv() returns [(verse_id, text, status, note)] for all 31,102 verses: the 16 verses
not in the ESV main text get empty text and a note, text lost at numbering differences is restored, '--' becomes an
em dash, stray curly quotes are straightened, and the dump's structural defects are repaired (repair()).
"""
import json, re
import cur_esv_patches as EP

ROW = re.compile(r"""^INSERT INTO "esv" \("verseid","book","chapter","versenumber","verse"\) VALUES """
                 r"""\((\d+),'((?:[^']|'')*)',(\d+),(\d+),'((?:[^']|'')*)'\);$""")
JOIN = re.compile(r'(?<=[a-z\)])([.!?;:,])([A-Z(\[])')

def tidy(t):
    return t.replace('--', '—').replace('“', '"').replace('”', '"')

def repair(vid, t):
    """Fix the dump's structural defects; returns (text, list of notes)."""
    notes = []
    b, c, v = vid.split('.')
    if b == 'Ps' and c == '119' and int(v) % 8 == 0:
        t2 = re.sub(r'\s*(' + '|'.join(map(re.escape, EP.PS119_LETTERS)) + r')$', '', t)
        if t2 != t: t = t2; notes.append('Psalm 119 stanza heading removed from the end of the verse.')
    if vid in EP.MOVE_TO_NOTE:
        frag = EP.MOVE_TO_NOTE[vid]; assert t.endswith(frag), vid
        t = t[:-len(frag)]; notes.append(frag.strip(' []').rstrip('.') + '.')
    if vid in EP.UNBRACKET:
        assert t.count('[') == 1 and t.endswith(']'), vid
        t = t.replace('[', ' ').rstrip(']'); notes.append(EP.UNBRACKET[vid])
    if JOIN.search(t):
        if vid in EP.QUOTE_JOINS:
            t = JOIN.sub(lambda m: m[1] + '" "' + m[2] if t[:m.start()].count('"') % 2 else m[1] + ' ' + m[2], t)
            notes.append('Quotation marks lost by the import were restored (checked against esv.org).')
        else:
            t = JOIN.sub(lambda m: m[1] + ' ' + m[2], t)
        t = re.sub(r'  +', ' ', t)
    return t, notes

def load_esv(dump, theo):
    osis_books = [b['fields']['osisName'] for b in sorted(json.load(open(f'{theo}/books.json')),
                                                           key=lambda b: int(b['fields']['bookOrder']))]
    rows, dump_books, skipped = [], [], 0
    for line in open(dump, encoding='utf-8'):
        if not line.startswith('INSERT'): continue
        m = ROW.match(line.rstrip('\n'))
        if not m: skipped += 1; continue
        b = m[2].replace("''", "'")
        if b not in dump_books: dump_books.append(b)
        rows.append((b, int(m[3]), int(m[4]), m[5].replace("''", "'")))
    assert skipped == 0 and len(dump_books) == 66, (skipped, len(dump_books))
    code = dict(zip(dump_books, osis_books))
    text = {f'{code[b]}.{c}.{v}': t for b, c, v, t in rows}
    assert len(text) == 31102

    out = []
    for vid, t in text.items():
        status, note = 'as imported', EP.NOTES.get(vid)
        if vid in EP.NOT_IN_ESV:
            assert t == 'See Footnote' or vid == 'Matt.17.21', (vid, t)
            footnote = f' Some manuscripts add: "{t}"' if t != 'See Footnote' else ''
            t, status, note = '', 'not in text', EP.NOT_IN_ESV_NOTE + footnote
        elif vid in EP.PATCHES:
            how, extra, note = EP.PATCHES[vid]
            assert how == 'append' and extra.strip() not in t
            t, status = t + extra, 'patched'
        elif t == 'See Footnote':
            raise SystemExit(f'unexpected placeholder at {vid}')
        tidied = tidy(t)
        if tidied != t and status == 'as imported': status = 'typography fixed'
        repaired, fixes = repair(vid, tidied)
        if repaired != tidied:
            if status in ('as imported', 'typography fixed'): status = 'defect fixed'
            note = ' '.join(filter(None, [note] + fixes)) or None
        out.append((vid, repaired, status, note))
    return out
