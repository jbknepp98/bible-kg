-- Authors and works (library bible-sources): who wrote, preached or edited the documents in the graph, and the larger
-- works those documents carry. Schema only, safe to re-run. Rows are added through the document-core service after a
-- person approves them (writer login bible_sources_writer); source/export_sources.py dumps them to
-- migrations/08_sources_data.sql so a rebuilt database gets them back.
-- Documents live in the doccore database, so document_id columns are checked for format only.
SET search_path TO bible;
BEGIN;

CREATE TABLE IF NOT EXISTS author (
  author_id varchar(80) PRIMARY KEY CHECK (author_id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  display_name varchar(200) NOT NULL CHECK (display_name !~ '[()]' AND display_name !~ '[0-9]+:[0-9]+'),
  also_known_as text,
  honorifics varchar(80),
  author_kind varchar(12) NOT NULL CHECK (author_kind IN ('Person', 'Organization')),
  year_of_birth varchar(10),
  year_of_death varchar(10),
  tradition varchar(20) CHECK (tradition IN ('Reformed', 'Presbyterian', 'Baptist', 'Anglican', 'Lutheran', 'Methodist',
                                             'Puritan', 'Pentecostal', 'Nondenominational', 'Other')),
  denomination varchar(120),
  vocation varchar(200),
  affiliations text,
  nationality varchar(80),
  summary_of_life text,
  summary_source text,
  wikidata_id varchar(20) CHECK (wikidata_id ~ '^Q[0-9]+$'),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS work (
  work_id varchar(80) PRIMARY KEY CHECK (work_id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  display_name varchar(200) NOT NULL CHECK (display_name !~ '[()]' AND display_name !~ '[0-9]+:[0-9]+'),
  also_known_as text,
  work_type varchar(20) NOT NULL CHECK (work_type IN ('Sermon', 'SermonSeries', 'Book', 'Commentary', 'CommentarySeries',
                                                      'Lecture', 'Article', 'Hymn', 'Confession', 'Catechism', 'Letter',
                                                      'Course', 'Episode')),
  date_label varchar(40),
  year varchar(4) CHECK (year ~ '^[0-9]{4}$'),
  occasion text,
  language varchar(20),
  work_summary text,
  wikidata_id varchar(20) CHECK (wikidata_id ~ '^Q[0-9]+$'),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS work_part (
  work_id varchar(80) NOT NULL REFERENCES work,
  parent_work_id varchar(80) NOT NULL REFERENCES work,
  part_label varchar(80),
  part_order integer NOT NULL DEFAULT 1 CHECK (part_order >= 1),
  PRIMARY KEY (work_id, parent_work_id),
  CHECK (work_id <> parent_work_id)
);

CREATE TABLE IF NOT EXISTS work_credit (
  work_id varchar(80) NOT NULL REFERENCES work,
  author_id varchar(80) NOT NULL REFERENCES author,
  contribution_role varchar(20) NOT NULL CHECK (contribution_role IN ('Author', 'Preacher', 'Commentator', 'Editor',
                                                                     'Translator', 'Compiler', 'Transcriber')),
  credit_order integer NOT NULL DEFAULT 1 CHECK (credit_order >= 1),
  credited_as varchar(200),
  PRIMARY KEY (work_id, author_id, contribution_role)
);

CREATE TABLE IF NOT EXISTS document_credit (
  document_id varchar(80) NOT NULL CHECK (document_id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  author_id varchar(80) NOT NULL REFERENCES author,
  contribution_role varchar(20) NOT NULL CHECK (contribution_role IN ('Author', 'Preacher', 'Commentator', 'Editor',
                                                                     'Translator', 'Compiler', 'Transcriber')),
  credit_order integer NOT NULL DEFAULT 1 CHECK (credit_order >= 1),
  credited_as varchar(200),
  PRIMARY KEY (document_id, author_id, contribution_role)
);

CREATE TABLE IF NOT EXISTS document_work (
  document_id varchar(80) NOT NULL CHECK (document_id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  work_id varchar(80) NOT NULL REFERENCES work,
  portion varchar(20) NOT NULL CHECK (portion IN ('Complete', 'Excerpt', 'Abridgement', 'Transcript', 'Translation', 'Outline')),
  locator varchar(200),
  PRIMARY KEY (document_id, work_id)
);

CREATE TABLE IF NOT EXISTS work_passage (
  work_id varchar(80) NOT NULL REFERENCES work,
  book_id varchar(8) REFERENCES book,
  chapter_id varchar(16) REFERENCES chapter,
  verse_id varchar(20) REFERENCES verse,
  passage_label varchar(120) NOT NULL,
  CHECK (num_nonnulls(book_id, chapter_id, verse_id) = 1),
  UNIQUE NULLS NOT DISTINCT (work_id, book_id, chapter_id, verse_id)
);

-- Views for Connect. Text columns are COALESCEd to '' (empty text compiles fine; integers here are NOT NULL).
CREATE OR REPLACE VIEW v_atlas_author AS
SELECT author_id, display_name, COALESCE(also_known_as, '') AS also_known_as, COALESCE(honorifics, '') AS honorifics,
       author_kind, COALESCE(year_of_birth, '') AS year_of_birth, COALESCE(year_of_death, '') AS year_of_death,
       COALESCE(tradition, '') AS tradition, COALESCE(denomination, '') AS denomination, COALESCE(vocation, '') AS vocation,
       COALESCE(affiliations, '') AS affiliations, COALESCE(nationality, '') AS nationality,
       COALESCE(summary_of_life, '') AS summary_of_life, COALESCE(summary_source, '') AS summary_source,
       COALESCE(wikidata_id, '') AS wikidata_id
FROM author;

CREATE OR REPLACE VIEW v_atlas_work AS
SELECT work_id, display_name, COALESCE(also_known_as, '') AS also_known_as, work_type, COALESCE(date_label, '') AS date_label,
       COALESCE(year, '') AS year, COALESCE(occasion, '') AS occasion, COALESCE(language, '') AS language,
       COALESCE(work_summary, '') AS work_summary, COALESCE(wikidata_id, '') AS wikidata_id
FROM work;

CREATE OR REPLACE VIEW v_atlas_work_part AS
SELECT work_id, parent_work_id, COALESCE(part_label, '') AS part_label, part_order FROM work_part;

CREATE OR REPLACE VIEW v_atlas_work_credit AS
SELECT work_id, author_id, contribution_role, credit_order, COALESCE(credited_as, '') AS credited_as FROM work_credit;

CREATE OR REPLACE VIEW v_atlas_document_credit AS
SELECT document_id, author_id, contribution_role, credit_order, COALESCE(credited_as, '') AS credited_as FROM document_credit;

CREATE OR REPLACE VIEW v_atlas_document_work AS
SELECT document_id, work_id, portion, COALESCE(locator, '') AS locator FROM document_work;

-- one row per expounded passage, with the target split so maps can build Bible.Book.<b>[.<c>[.<v>]] instance ids
CREATE OR REPLACE VIEW v_atlas_work_passage AS
SELECT p.work_id, 'Book' AS target_kind, p.book_id, NULL::integer AS chapter_number, NULL::integer AS verse_number, p.passage_label
FROM work_passage p WHERE p.book_id IS NOT NULL
UNION ALL
SELECT p.work_id, 'Chapter', c.book_id, c.chapter_number, NULL, p.passage_label
FROM work_passage p JOIN chapter c ON c.chapter_id = p.chapter_id
UNION ALL
SELECT p.work_id, 'Verse', v.book_id, v.chapter_number, v.verse_number, p.passage_label
FROM work_passage p JOIN verse v ON v.verse_id = p.verse_id;

-- writer login for the document-core service (password set from doccore.env by the operator, never in this file)
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'bible_sources_writer') THEN CREATE ROLE bible_sources_writer LOGIN; END IF;
END $$;
GRANT USAGE ON SCHEMA bible TO bible_sources_writer;
GRANT SELECT, INSERT, UPDATE ON author, work, work_part, work_credit, document_credit, document_work, work_passage TO bible_sources_writer;
GRANT SELECT ON book, chapter, verse TO bible_sources_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA bible TO timebase_reader;
COMMIT;
