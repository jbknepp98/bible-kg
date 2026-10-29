-- Phase 2 verification (Postgres). Every "mismatch" / "bad" row must be 0.
-- Run: docker exec -i bible-pg psql -U bible_admin -d bible < verify/phase2.sql
SET search_path TO bible;
SELECT check_name, actual, expected, CASE WHEN actual = expected THEN 'ok' ELSE 'FAIL' END AS result FROM (VALUES
 ('book',                    (SELECT count(*) FROM book), 66),
 ('chapter',                 (SELECT count(*) FROM chapter), 1189),
 ('verse',                   (SELECT count(*) FROM verse), 31102),
 ('verse_text',              (SELECT count(*) FROM verse_text), 31102),
 ('place',                   (SELECT count(*) FROM place), 1298),
 ('place with coordinates',  (SELECT count(*) FROM place WHERE latitude IS NOT NULL), 1267),
 ('verse_place',             (SELECT count(*) FROM verse_place), 7534),
 ('verse_person',            (SELECT count(*) FROM verse_person), 20366),   -- 19,249 Theographic + 1,117 curated unnamed
 ('verse_being',             (SELECT count(*) FROM verse_being), 402),
 ('verse_divine',            (SELECT count(*) FROM verse_divine), 8833),     -- God 8,587 + Holy Spirit 246
 ('place_relation',          (SELECT count(*) FROM place_relation), 644),
 ('person_place',            (SELECT count(*) FROM person_place), 584),
 ('book_writer',             (SELECT count(*) FROM book_writer), 76),   -- 77 minus Hebrews (authorship Unknown)
 ('person',                  (SELECT count(*) FROM person), 3132),
 ('relationship',            (SELECT count(*) FROM relationship), 5209),
 ('spiritual_being',         (SELECT count(*) FROM spiritual_being), 60),
 ('spiritual_relationship',  (SELECT count(*) FROM spiritual_relationship), 73),
 ('divine / manifestation',  (SELECT count(*) FROM divine) + (SELECT count(*) FROM manifestation), 20),
 ('chapters with wrong verse_count', (SELECT count(*) FROM chapter c WHERE c.verse_count <> (SELECT count(*) FROM verse v WHERE v.chapter_id = c.chapter_id)), 0),
 ('books with wrong verse_count',    (SELECT count(*) FROM book b WHERE b.verse_count <> (SELECT count(*) FROM verse v WHERE v.book_id = b.book_id)), 0),
 ('people verse_count mismatch',     (SELECT count(*) FROM person p WHERE p.verse_count <> (SELECT count(*) FROM verse_person x WHERE x.person_id = p.person_id)), 0),
 ('beings verse_count mismatch',     (SELECT count(*) FROM spiritual_being b WHERE b.verse_count <> (SELECT count(*) FROM verse_being x WHERE x.being_id = b.being_id)), 0),
 ('God/Holy Spirit verse mismatch',  (SELECT count(*) FROM divine d WHERE d.verse_count <> (SELECT count(*) FROM verse_divine x WHERE x.divine_id = d.divine_id)), 0),
 ('places verse_count mismatch',     (SELECT count(*) FROM place p WHERE p.verse_count <> (SELECT count(*) FROM verse_place x WHERE x.place_id = p.place_id)), 0),
 ('names with parentheses or refs',  (SELECT count(*) FROM person WHERE display_name ~ '[()]|[0-9]+:[0-9]+')
                                   + (SELECT count(*) FROM place  WHERE display_name ~ '[()]|[0-9]+:[0-9]+'), 0),
 ('David verses',  (SELECT count(*) FROM verse_person WHERE person_id = 'david_994'), 896),
 ('Jesus verses',  (SELECT count(*) FROM verse_person WHERE person_id = 'jesus_905'), 1831),
 ('Moses verses',  (SELECT count(*) FROM verse_person WHERE person_id = 'moses_2108'), 774),
 ('Ruth verses',   (SELECT count(*) FROM verse_person WHERE person_id = 'ruth_2450'), 13)
) AS t(check_name, actual, expected);
