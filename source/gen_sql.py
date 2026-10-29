import json, os
D = json.load(open('/home/claude/work/final.json'))
OUT = '/mnt/user-data/outputs/bible-project/initdb'
os.makedirs(OUT, exist_ok=True)

REL_TYPES = [
 # code, category, is_symmetric, description
 ("Begot","Family",False,"Subject is a parent (father or mother) of the object."),
 ("Married","Family",True,"Subject and object were husband and wife (includes concubines where the source records a union)."),
 ("SiblingOf","Family",True,"Subject and object share both parents (full siblings)."),
 ("HalfSiblingOf","Family",True,"Subject and object share one parent."),
 ("Adopted","Family",False,"Subject raised the object as their own child."),
 ("Succeeded","Office",False,"Subject succeeded the object in an office (throne, priesthood, prophetic or apostolic office)."),
 ("Anointed","Office",False,"Subject anointed the object for an office (king, priest)."),
 ("Appointed","Office",False,"Subject appointed the object to a position or task."),
 ("Commissioned","Office",False,"Subject charged, sent or called the object to a mission."),
 ("Served","Allegiance",False,"Subject served the object as servant, official, soldier or assistant."),
 ("Followed","Allegiance",False,"Subject followed the object as disciple, adherent or loyal supporter."),
 ("Accompanied","Allegiance",False,"Subject travelled with or ministered alongside the object."),
 ("Mentored","Allegiance",False,"Subject taught, trained or guided the object."),
 ("Opposed","Conflict",False,"Subject opposed, conspired against or rebelled against the object."),
 ("Pursued","Conflict",False,"Subject hunted or chased the object."),
 ("Defeated","Conflict",False,"Subject defeated the object (or the object's forces) in battle."),
 ("Captured","Conflict",False,"Subject took the object captive."),
 ("Imprisoned","Conflict",False,"Subject put the object in prison or custody."),
 ("Exiled","Conflict",False,"Subject banished or expelled the object."),
 ("Sentenced","Conflict",False,"Subject condemned or ordered the execution or punishment of the object."),
 ("Killed","Conflict",False,"Subject killed the object, directly or by order."),
 ("Betrayed","Conflict",False,"Subject betrayed the trust of the object."),
 ("Deceived","Conflict",False,"Subject deliberately misled the object."),
 ("Denied","Conflict",False,"Subject publicly disowned the object."),
 ("Freed","Deliverance",False,"Subject released the object from captivity, prison or slavery."),
 ("Rescued","Deliverance",False,"Subject saved or protected the object from danger."),
 ("Healed","Deliverance",False,"Subject healed the object of illness or affliction."),
 ("RaisedFromDead","Deliverance",False,"Subject raised the object from death."),
 ("Baptized","Religious",False,"Subject baptized the object."),
 ("Blessed","Religious",False,"Subject pronounced a blessing on the object."),
 ("Cursed","Religious",False,"Subject pronounced a curse or judgment on the object."),
 ("Rebuked","Religious",False,"Subject rebuked or confronted the object for wrongdoing."),
 ("WroteTo","Religious",False,"Subject addressed a letter or book to the object."),
]

DDL = r"""
-- Bible People Knowledge Graph : schema
-- Years: signed integers, negative = BC, positive = AD (approximate). Labels provided for display.
CREATE SCHEMA IF NOT EXISTS bible;
SET search_path TO bible;

CREATE TABLE person (
  person_id                  varchar(64)  PRIMARY KEY,
  first_name                 varchar(80)  NOT NULL,
  family_name                varchar(80),
  display_name               varchar(160) NOT NULL UNIQUE,
  also_known_as              text,
  gender                     varchar(10)  NOT NULL CHECK (gender IN ('Male','Female')),
  place_of_birth             varchar(120),
  place_of_death             varchar(120),
  year_of_birth              integer,
  year_of_death              integer,
  year_of_birth_label        varchar(20),
  year_of_death_label        varchar(20),
  manner_of_death            varchar(200),
  testament                  varchar(20)  NOT NULL CHECK (testament IN ('Old Testament','New Testament')),
  appears_in_both_testaments boolean      NOT NULL DEFAULT false,
  tribe                      varchar(40),
  affiliations               varchar(200),
  summary_of_life            text         NOT NULL,
  summary_source             varchar(40)  NOT NULL,
  first_reference            varchar(40),
  verse_count                integer      NOT NULL DEFAULT 0,
  source_record_id           varchar(32),
  roles                      varchar(80),
  primary_role               varchar(20)  NOT NULL DEFAULT 'Person'
                             CHECK (primary_role IN ('Person','King','Prophet','Priest','Judge','Apostle'))
);

CREATE TABLE king (
  person_id           varchar(64) PRIMARY KEY REFERENCES person(person_id),
  royal_title         varchar(40) NOT NULL,
  kingdom             varchar(80) NOT NULL,
  dynasty             varchar(60),
  reign_start_year    integer,
  reign_end_year      integer,
  reign_start_label   varchar(20),
  reign_end_label     varchar(20),
  reign_length_years  integer,
  assessment          varchar(20) NOT NULL
);

CREATE TABLE prophet (
  person_id           varchar(64) PRIMARY KEY REFERENCES person(person_id),
  prophet_class       varchar(30) NOT NULL,
  books_authored      varchar(120),
  ministry_start_year integer,
  ministry_end_year   integer,
  audience            varchar(80),
  is_true_prophet     boolean NOT NULL
);

CREATE TABLE priest (
  person_id         varchar(64) PRIMARY KEY REFERENCES person(person_id),
  priestly_order    varchar(60) NOT NULL,
  is_high_priest    boolean NOT NULL,
  served_at         varchar(80),
  tenure_start_year integer,
  tenure_end_year   integer
);

CREATE TABLE judge (
  person_id      varchar(64) PRIMARY KEY REFERENCES person(person_id),
  judge_order    integer NOT NULL,
  tribe_of_origin varchar(40),
  years_judged   integer,
  oppressor      varchar(80),
  start_year     integer
);

CREATE TABLE apostle (
  person_id         varchar(64) PRIMARY KEY REFERENCES person(person_id),
  apostle_group     varchar(40) NOT NULL,
  prior_occupation  varchar(60),
  calling_reference varchar(40),
  death_tradition   varchar(120)
);

CREATE TABLE relationship_type (
  relationship_type varchar(30) PRIMARY KEY,
  category          varchar(20) NOT NULL,
  is_symmetric      boolean NOT NULL,
  description       text NOT NULL
);

CREATE TABLE relationship (
  relationship_id     integer PRIMARY KEY,
  from_person_id      varchar(64) NOT NULL REFERENCES person(person_id),
  relationship_type   varchar(30) NOT NULL REFERENCES relationship_type(relationship_type),
  to_person_id        varchar(64) NOT NULL REFERENCES person(person_id),
  scripture_reference varchar(80),
  source              varchar(20) NOT NULL,
  notes               varchar(200),
  CONSTRAINT relationship_unique UNIQUE (from_person_id, relationship_type, to_person_id),
  CONSTRAINT relationship_no_self CHECK (from_person_id <> to_person_id)
);
CREATE INDEX ix_rel_from ON relationship(from_person_id);
CREATE INDEX ix_rel_to   ON relationship(to_person_id);
CREATE INDEX ix_rel_type ON relationship(relationship_type);
CREATE INDEX ix_person_name ON person(first_name);

-- Convenience views for Connect / Atlas
CREATE VIEW v_person_roles AS
SELECT p.person_id, p.display_name,
       (k.person_id IS NOT NULL) AS is_king,
       (pr.person_id IS NOT NULL) AS is_prophet,
       (pt.person_id IS NOT NULL) AS is_priest,
       (j.person_id IS NOT NULL) AS is_judge,
       (a.person_id IS NOT NULL) AS is_apostle
FROM person p
LEFT JOIN king k     ON k.person_id = p.person_id
LEFT JOIN prophet pr ON pr.person_id = p.person_id
LEFT JOIN priest pt  ON pt.person_id = p.person_id
LEFT JOIN judge j    ON j.person_id = p.person_id
LEFT JOIN apostle a  ON a.person_id = p.person_id;

CREATE VIEW v_relationship_named AS
SELECT r.relationship_id, r.from_person_id, f.display_name AS from_name, r.relationship_type,
       r.to_person_id, t.display_name AS to_name, r.scripture_reference, r.source, rt.category
FROM relationship r
JOIN person f ON f.person_id = r.from_person_id
JOIN person t ON t.person_id = r.to_person_id
JOIN relationship_type rt ON rt.relationship_type = r.relationship_type;

-- One flat view per Atlas entity type. Each person appears in exactly one view (by primary_role);
-- the full role list is kept in person.roles.
CREATE VIEW v_atlas_person AS
SELECT p.* FROM person p WHERE p.primary_role = 'Person';
CREATE VIEW v_atlas_king AS
SELECT p.*, k.royal_title, k.kingdom, k.dynasty, k.reign_start_year, k.reign_end_year,
       k.reign_start_label, k.reign_end_label, k.reign_length_years, k.assessment
FROM person p JOIN king k USING (person_id) WHERE p.primary_role = 'King';
CREATE VIEW v_atlas_prophet AS
SELECT p.*, x.prophet_class, x.books_authored, x.ministry_start_year, x.ministry_end_year, x.audience, x.is_true_prophet
FROM person p JOIN prophet x USING (person_id) WHERE p.primary_role = 'Prophet';
CREATE VIEW v_atlas_priest AS
SELECT p.*, x.priestly_order, x.is_high_priest, x.served_at, x.tenure_start_year, x.tenure_end_year
FROM person p JOIN priest x USING (person_id) WHERE p.primary_role = 'Priest';
CREATE VIEW v_atlas_judge AS
SELECT p.*, x.judge_order, x.tribe_of_origin, x.years_judged, x.oppressor, x.start_year AS judgeship_start_year
FROM person p JOIN judge x USING (person_id) WHERE p.primary_role = 'Judge';
CREATE VIEW v_atlas_apostle AS
SELECT p.*, x.apostle_group, x.prior_occupation, x.calling_reference, x.death_tradition
FROM person p JOIN apostle x USING (person_id) WHERE p.primary_role = 'Apostle';
CREATE VIEW v_atlas_relationship AS
SELECT r.relationship_id, r.from_person_id, r.relationship_type, r.to_person_id,
       COALESCE(r.scripture_reference, '') AS scripture_reference, r.source
FROM relationship r;

-- Read-only login for Timebase Connect
CREATE ROLE timebase_reader LOGIN;  -- password set by initdb/99_reader_password.sh from TIMEBASE_READER_PASSWORD (bible.env)
GRANT USAGE ON SCHEMA bible TO timebase_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA bible TO timebase_reader;
"""

def esc(v):
    if v is None: return r'\N'
    if isinstance(v, bool): return 't' if v else 'f'
    s = str(v)
    return s.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')

def copy(table, cols, rows):
    out = [f"COPY bible.{table} ({', '.join(cols)}) FROM stdin;"]
    for r in rows: out.append('\t'.join(esc(r.get(c)) for c in cols))
    out.append('\\.\n')
    return '\n'.join(out)

PCOLS = ['person_id','first_name','family_name','display_name','also_known_as','gender','place_of_birth','place_of_death',
         'year_of_birth','year_of_death','year_of_birth_label','year_of_death_label','manner_of_death','testament',
         'appears_in_both_testaments','tribe','affiliations','summary_of_life','summary_source','first_reference','verse_count','source_record_id','roles','primary_role']
parts = ["-- Bible People Knowledge Graph : data\nSET client_encoding = 'UTF8';\n",
  copy('person', PCOLS, D['person']),
  copy('king', ['person_id','royal_title','kingdom','dynasty','reign_start_year','reign_end_year','reign_start_label','reign_end_label','reign_length_years','assessment'], D['king']),
  copy('prophet', ['person_id','prophet_class','books_authored','ministry_start_year','ministry_end_year','audience','is_true_prophet'], D['prophet']),
  copy('priest', ['person_id','priestly_order','is_high_priest','served_at','tenure_start_year','tenure_end_year'], D['priest']),
  copy('judge', ['person_id','judge_order','tribe_of_origin','years_judged','oppressor','start_year'], D['judge']),
  copy('apostle', ['person_id','apostle_group','prior_occupation','calling_reference','death_tradition'], D['apostle']),
  copy('relationship_type', ['relationship_type','category','is_symmetric','description'],
       [dict(zip(['relationship_type','category','is_symmetric','description'], t)) for t in REL_TYPES]),
  copy('relationship', ['relationship_id','from_person_id','relationship_type','to_person_id','scripture_reference','source','notes'], D['relationship']),
  "ANALYZE;\n"]
open(f'{OUT}/01_schema.sql', 'w').write(DDL)
open(f'{OUT}/02_data.sql', 'w').write('\n'.join(parts))
used = {r['relationship_type'] for r in D['relationship']}
missing = used - {t[0] for t in REL_TYPES}
print('missing rel types:', missing)
