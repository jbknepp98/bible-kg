-- Phase 3 (events) verification (Postgres). Every row must say ok.
-- Run: docker exec -i bible-pg psql -U bible_admin -d bible < verify/phase3.sql
SET search_path TO bible;
SELECT check_name, actual, expected, CASE WHEN actual = expected THEN 'ok' ELSE 'FAIL' END AS result FROM (VALUES
 ('event',                       (SELECT count(*) FROM event), 450),
 ('event_verse',                 (SELECT count(*) FROM event_verse), 17570),
 ('event_participant',           (SELECT count(*) FROM event_participant), 881),
 ('  of which God / Holy Spirit', (SELECT count(*) FROM event_participant WHERE participant_kind = 'Divine'), 30),
 ('  of which spiritual beings', (SELECT count(*) FROM event_participant WHERE participant_kind = 'SpiritualBeing'), 2),
 ('event_place',                 (SELECT count(*) FROM event_place), 476),
 ('event_relation SubEventOf',   (SELECT count(*) FROM event_relation WHERE relation_type = 'SubEventOf'), 202),
 ('event_relation Follows',      (SELECT count(*) FROM event_relation WHERE relation_type = 'Follows'), 392),
 ('events with exact dates',     (SELECT count(*) FROM event WHERE start_date IS NOT NULL), 50),
 ('events with wrong verse_count', (SELECT count(*) FROM event e WHERE e.verse_count <> (SELECT count(*) FROM event_verse x WHERE x.event_id = e.event_id)), 0),
 ('event names breaking naming rules', (SELECT count(*) FROM event WHERE display_name ~ '[()]|[0-9]+:[0-9]+'), 0),
 ('end before start',            (SELECT count(*) FROM event WHERE end_year < start_year), 0)
) AS t(check_name, actual, expected);
-- Atlas (ExecuteCypherQuery, domain Bible-Project): Event 450; attestedIn 17570, involves 881, occurredAt 476,
-- subEventOf 202, follows 392:
--   MATCH (e:`urn:atlas:ontology:bible-events:Event`)-[r]->(t) WITH type(r) AS rel, count(*) AS n
--   WHERE rel STARTS WITH 'urn:atlas:ontology:bible-events:' RETURN rel, n ORDER BY n DESC
