-- Translations and footnotes verification (Postgres). Every row must say ok. Needs 06 and 91 applied.
-- Note names may contain references: for a citation note the reference is the content.
-- Run: docker exec -i bible-pg psql -U bible_admin -d bible < verify/translations.sql
SET search_path TO bible;
SELECT check_name, actual, expected, CASE WHEN actual = expected THEN 'ok' ELSE 'FAIL' END AS result FROM (VALUES
 ('translations',                 (SELECT count(*) FROM translation), 4),
 ('KJV verses',                   (SELECT count(*) FROM verse_text WHERE translation = 'KJV'), 31102),
 ('BSB verses',                   (SELECT count(*) FROM verse_text WHERE translation = 'BSB'), 31102),
 ('ESV verses',                   (SELECT count(*) FROM verse_text WHERE translation = 'ESV'), 31102),
 ('NET verses',                   (SELECT count(*) FROM verse_text WHERE translation = 'NET'), 31102),
 ('ESV not in text',              (SELECT count(*) FROM verse_text WHERE translation = 'ESV' AND status = 'not in text'), 16),
 ('empty text not marked',        (SELECT count(*) FROM verse_text WHERE text = '' AND status NOT IN ('not in text', 'merged into previous')), 0),
 ('BSB notes',                    (SELECT count(*) FROM note WHERE translation = 'BSB'), 4846),
 ('NET notes',                    (SELECT count(*) FROM note WHERE translation = 'NET'), 38),
 ('note names with brackets', (SELECT count(*) FROM note WHERE display_name ~ '[()]'), 0),
 ('verse citations',              (SELECT count(*) FROM verse_citation), 443),
 ('citations within the OT',      (SELECT count(*) FROM verse_citation c JOIN verse v ON v.verse_id = c.to_verse_id JOIN book b USING (book_id) WHERE b.testament = 'Old Testament'), 6),
 ('citations to an earlier verse only', (SELECT count(*) FROM verse_citation c JOIN verse a ON a.verse_id = c.from_verse_id JOIN verse b ON b.verse_id = c.to_verse_id WHERE b.verse_sort <= a.verse_sort), 0),
 ('translation view rows',        (SELECT count(*) FROM v_atlas_verse_translation), 31102)
) AS t(check_name, actual, expected);
-- Atlas (ExecuteCypherQuery, domain Bible-Project): Note 4884, hasNote 4884, citedIn 443.
--   MATCH (v:Verse)-[:hasNote]->(n:Note) RETURN n.Translation AS tr, count(*) AS c
--   MATCH ()-[r:citedIn]->() RETURN count(r) AS citedIn
