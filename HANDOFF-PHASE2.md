# Bible-Project Phase 2 handoff: Books, Chapters, Verses, Places
> **Adjustments applied 2026-10-29 (Claude Code).** These override the sections below where they conflict.
> - Project path is `~/Documents/bible-project`.
> - Naming rules from Phase 1 apply to places: no parentheses, no scripture references (`source/cur_place_names.py`).
> - Baseline is no longer the Phase 1 numbers: 3,132 people, 5,209 relationships, 60 spiritual beings (73 edges),
>   God / 3 divine persons / 16 manifestations (`initdb/05_divine.sql`, 43 edges).
> - `migrations/04_phase2_adjustments.sql` (from `source/gen_phase2_adjust.py`) runs after `03_text_places.sql`:
>   place renames; `verse_being` (402: Theographic links of the excluded beings, Lucifer folded into Satan, plus
>   curated passages); `verse_divine` (8,833: God 8,587, Holy Spirit 246); verse links for the 82 curated unnamed people.
> - Apply order on an existing database: `initdb/04_spirits.sql`, `initdb/05_divine.sql`, `migrations/03_text_places.sql`,
>   `migrations/04_phase2_adjustments.sql` (each rebuilds its own objects). Verify with `verify/phase2.sql` (29 checks).
> - **Done 2026-10-29.** Postgres verified (`verify/phase2.sql`, 29/29). Atlas: libraries `bible-places`, `bible-text`
>   built on branch `phase2-text`, Ruth pilot passed, full load compiled (~5 s, Atlas RAM 1.7 -> 1.9 GB), section 8 checks
>   passed (`verify/phase2.cypher`), merged to `main` (no conflicts; pre-merge main was 3be28fd). main: 36,873 instances,
>   80,637 edges, 358,409 properties, validation 0 errors.
> - Map changes vs section 6: places split by coordinate pattern (`Places/[Coords]` = Both/Theographic/OpenBible/None) and
>   verses split into `VersesDated/[Book]` / `VersesUndated/[Book]`, because Atlas cannot compile an empty value into a
>   number; extra mention topics `VerseBeings/[Book]`, `VerseDivine/[Book]`; `mentions` targets Person, Place,
>   SpiritualBeing, Godhead, DivinePerson. Book composition years are defined but not mapped until curated.


For Claude Code. Phase 1 (people) is live in Atlas domain `Bible-Project`. Phase 2 adds the text spine and places, then links every person and place to every verse that names them. Everything here is additive: no Phase 1 table, library or instance map changes.

## 0. Rules for this phase

1. **Work on an Atlas branch.** Create `phase2-text` and do every Atlas change there. Merge to `main` only after section 8 passes.
2. **Back up first.** `docker exec bible-pg pg_dump -U bible_admin -Fc bible > ~/Projects/bible-project/backups/bible-pre-phase2.dump` and export library `bible-people` with Atlas MCP `GetLibraryExportJson`.
3. **Record the baseline.** People 3,050 (Person 2,780, King 141, Prophet 62, Priest 34, Judge 14, Apostle 19), relationships 5,129, `contains` 3,052, domain validation errors 0. These must be unchanged at the end.
4. **Join on keys, never names.** Every person link uses `person_id` (e.g. `david_994`), every place link uses `place_id` (e.g. `jerusalem_636`), every verse uses the OSIS id (e.g. `Gen.1.1`). The ETL does this; do not add name matching anywhere.
5. **Migrations, not initdb.** The container is already initialized. Apply `migrations/03_text_places.sql` with `psql`. It is idempotent: it drops and recreates Phase 2 objects only.
6. **Pilot before full load.** Ruth end to end (section 6) before all 66 books.
7. **Prefer MCP.** Use Timebase_Atlas / Timebase_Connect MCP tools where they expose the operation; fall back to REST with the same Pulse client only where they don't.

Preflight check: confirm Phase 1 Person instance IDs are `Bible.Person.<person_id>`. Every `mentions` and `bornIn` target below assumes that pattern. If yours differ, change the target templates, not the data.

## 1. What's in the bundle

| Path | Purpose |
|---|---|
| `migrations/03_text_places.sql` | DDL + data + views for Phase 2. Tested twice in a row on Postgres 16 on top of the Phase 1 database |
| `source/etl_text_places.py` | Generates the migration from Theographic JSON + Phase 1 `final.json`: `python3 -I etl_text_places.py <theographic/json> <final.json> <out.sql>` |
| `source/*.py` (Phase 1) | Unchanged |

Source data: Theographic Bible Metadata (github.com/robertrouse/theographic-bible-metadata, **CC BY-SA 4.0**: anything Flow publishes from this must carry the same license and attribution). Verse text: KJV (public domain), carried in Theographic.

## 2. Postgres model (schema `bible`, new objects)

| Table | Key | Rows | Notes |
|---|---|---|---|
| `book` | `book_id` (OSIS, `Gen`) | 66 | name, short_name, book_order, testament, division, genre, original_language, chapter_count, verse_count, author_traditional, authorship_confidence, composition_year_start/end, composition_date_label, dating_basis, summary, source |
| `book_writer` | (book_id, person_id) | 77 | Traditional authors, from Theographic `writers` (comma lists split, duplicates removed) |
| `chapter` | `chapter_id` (`Gen.1`) | 1,189 | book_id, chapter_number, verse_count |
| `verse` | `verse_id` (`Gen.1.1`) | 31,102 | verse_sort (01001001), book_id, chapter_id, chapter_number, verse_number, reference_label ("Genesis 1:1"), approx_year (28,024 have one), dating_basis |
| `verse_text` | (verse_id, translation) | 31,102 | KJV now; add BSB later as more rows, no schema change. license, attribution per row |
| `place` | `place_id` | 1,298 | see section 4 |
| `verse_person` | (verse_id, person_id) | 19,249 | Theographic verse→people, excluding the 17 Phase 1 exclusions (God, Holy Spirit, Satan, angels, deities: 8,991 links dropped) |
| `verse_place` | (verse_id, place_id) | 7,534 | Theographic verse→places |
| `place_relation` | (from, type, to) | 644 | partOf 368, sameAs 257, near 19. sameAs and near stored once per pair |
| `person_place` | (person, type, place) | 584 | visited 462, bornIn 77, diedIn 45 |

Views for Connect: `v_atlas_book`, `v_atlas_book_writer`, `v_atlas_chapter`, `v_atlas_verse` (includes `text_kjv`), `v_atlas_verse_text`, `v_atlas_place`, `v_atlas_verse_person` (with book_id), `v_atlas_verse_place` (with book_id), `v_atlas_place_relation`, `v_atlas_person_place`. The migration re-grants SELECT to `timebase_reader`.

Curated in the ETL (review these): `genre` (Narrative, Law, Poetry, Wisdom, Prophecy, Apocalyptic, Gospel, Epistle), `original_language` (Daniel and Ezra are "Hebrew and Aramaic"), `authorship_confidence` (Stated in text / Traditional / Unknown; Hebrews = Unknown). Left NULL on purpose for later curation: composition dates, dating_basis, book summary, place modern_name and modern_country.

Apply:
```bash
cd ~/Projects/bible-project
docker exec -i bible-pg psql -U bible_admin -d bible -v ON_ERROR_STOP=1 < migrations/03_text_places.sql
```

## 3. Atlas libraries

Two new libraries, same conventions as `bible-people` (types and properties PascalCase, relationships camelCase, every type, property and relationship gets a comment, since Gage depends on them).

### `bible-places` (depends on `bible-people`)
- **Place** (one type; `FeatureType` is a property, not subtypes): PlaceId, Name, DisplayName, KjvName, EsvName, AlsoKnownAs, FeatureType, FeatureSubType, Latitude (double), Longitude (double), CoordinateSource, OpenBibleLatitude, OpenBibleLongitude, LocationPrecision, IdentificationStatus, ModernName, ModernCountry, Notes, Testament, VerseCount, FirstReference, Summary, SummarySource
- Relationships: `partOf` (Place→Place), `near` (Place→Place, symmetric), `sameAs`: reuse `atlas-common:sameAs` rather than defining a new one, `bornIn` / `diedIn` / `visited` (Person→Place)

### `bible-text` (depends on `bible-people`, `bible-places`)
- **Book**: BookId, Name, ShortName, BookOrder, Testament, Division, Genre, OriginalLanguage, ChapterCount, VerseCount, AuthorTraditional, AuthorshipConfidence, CompositionYearStart, CompositionYearEnd, CompositionDateLabel, DatingBasis, Summary
- **Chapter**: ChapterId, ChapterNumber, VerseCount
- **Verse**: VerseId, VerseSort, ReferenceLabel, ChapterNumber, VerseNumber, ApproxYear, DatingBasis, TextKjv
- **VerseText** (optional now, needed when a second translation arrives): Translation, Text, License, Attribution
- Relationships: `writtenBy` (Book→Person), `mentions` (Verse→Person and Verse→Place: one relationship with `targetUnion` [Person, Place]), `hasText` (Verse→VerseText). Containment uses `atlas-common:contains`.

Decision recorded: `TextKjv` lives on Verse for now, simple and queryable. When BSB is added, move to `VerseText` instances and keep `TextKjv` only if the UI needs it.

Run library validation to 0 errors before any instance maps.

## 4. Place field mapping (from Theographic)

| Column | Rule |
|---|---|
| display_name | Name if unique, else "Name (feature type, first reference)", e.g. "Ramah (city, 1 Samuel 1:19)" |
| feature_type | Theographic featureType, else `Unknown` (554 places). Counts: City 441, Region 118, Landmark 54, Mountain 45, Water 38, Valley 36, Island 11, Path 1 |
| latitude / longitude | Theographic's chosen coordinates, only when both exist (1,267). `coordinate_source = Theographic`. OpenBible coordinates kept separately |
| location_precision | Theographic `precision` as-is: Rough 348, Related-Surrounding 111, Related-Within 57, Unlocated 22, Precise 2, Center 2; else `Unknown` (756) |
| identification_status | Verified 181, Unverified 997, Not identifiable 96, Unknown 24. **Show this in any map view**; never draw an unverified site like a verified one |
| summary | Easton's text, cleaned, same rule as Person |
| sameAs | Separate records joined (Luz/Bethel, Jebus/Jerusalem). Never merge |

## 5. Connect: extend source `bible-pg` (con_445bf6)

Add topics, all with subscriptions disabled (static data). Template topics take the book so the pilot can load one book.

| Topic | SQL |
|---|---|
| `Books` | `SELECT * FROM bible.v_atlas_book ORDER BY book_order` |
| `BookWriters` | `SELECT * FROM bible.v_atlas_book_writer` |
| `Chapters/[Book]` | `SELECT * FROM bible.v_atlas_chapter WHERE book_id = @Book OR @Book = 'ALL' ORDER BY chapter_id` |
| `Verses/[Book]` | `SELECT * FROM bible.v_atlas_verse WHERE book_id = @Book OR @Book = 'ALL' ORDER BY verse_sort` |
| `VersePeople/[Book]` | `SELECT * FROM bible.v_atlas_verse_person WHERE book_id = @Book OR @Book = 'ALL'` |
| `VersePlaces/[Book]` | `SELECT * FROM bible.v_atlas_verse_place WHERE book_id = @Book OR @Book = 'ALL'` |
| `Places` | `SELECT * FROM bible.v_atlas_place ORDER BY place_id` |
| `PlaceRelations/[Type]` | `SELECT * FROM bible.v_atlas_place_relation WHERE relation_type = @Type` |
| `PersonPlaces/[Type]` | `SELECT * FROM bible.v_atlas_person_place WHERE relation_type = @Type` |

Parameters: `Book`, `Type` = string. Preview each topic (`preview` endpoint or MCP) before touching Atlas. Expected row counts are in section 8.

## 6. Instance maps (new files only)

| File | Definitions |
|---|---|
| `text.map.json` | `books` (rowset `bible-pg/Books`), `testament-contains-books`, `chapters`, `book-contains-chapters`, `verses`, `chapter-contains-verses`, `book-written-by` |
| `places.map.json` | `places-folder` (Folder `Bible.Places`, one-item map), `bible-contains-places-folder`, `places`, `places-folder-contains-places`, `place-part-of`, `place-near`, `place-same-as` |
| `place-links.map.json` | `person-born-in`, `person-died-in`, `person-visited` |
| `mentions.map.json` | `verse-mentions-people`, `verse-mentions-places` |

Instance ID patterns:
- Book `Bible.Book.[BookId]`, Chapter `Bible.Book.[BookId].[Ch]`, Verse `Bible.Book.[BookId].[Ch].[V]` (label "Genesis 1:1")
- Place `Bible.Place.[PlaceId]`
- Edges `<relationship>-[keys]`, e.g. `mentions-[VerseId]-[PersonId]`. Must be unique: use both ends
- Testament folders already exist from Phase 1 (`Bible.OldTestament`, `Bible.NewTestament`); books go under them

Verse id contains dots (`Gen.1.1`). Build verse instance IDs from book, chapter and verse columns, not by concatenating the OSIS string, and check that Atlas treats the dots as path separators the way you expect.

**Pilot: Ruth.** Bind the four book-filtered topics with `Ruth`, plus Books, Places (all 1,298: needed as targets) and person links. Compile. Expected for Ruth: 1 book, 4 chapters, 85 verses, 94 person mentions across 21 distinct people (Naomi, Ruth, Boaz, Elimelech, Mahlon, Chilion, Orpah, Obed, Jesse, David, Perez, Hezron, Ram, Amminadab, Nahshon, Salmon, Judah, Tamar, Rachel, Leah, Moab), 11 place mentions. Inspect a few verses in the Atlas UI. Fix the shape here. Then switch the bindings to `ALL`.

## 7. Full load

Switch to `ALL`, compile, watch compile time and memory. Scale: 33,656 new nodes, 61,744 new edges (counts below). If the compile struggles, split verse and mentions maps by testament.

## 8. Verification (all must pass before merging to main)

### Postgres (already verified on a test load)
| Check | Expected |
|---|---|
| book / chapter / verse / verse_text | 66 / 1,189 / 31,102 / 31,102 |
| place | 1,298 (1,267 with coordinates) |
| verse_person / verse_place | 19,249 / 7,534 |
| place_relation | 644 (partOf 368, sameAs 257, near 19) |
| person_place | 584 (visited 462, bornIn 77, diedIn 45) |
| book_writer | 77 |
| Chapters and books whose verse_count disagrees with actual verses | 0 / 0 |
| People whose `verse_count` ≠ their verse_person rows | **0** (all 3,050) |
| Places whose `verse_count` ≠ their verse_place rows | **0** (all 1,298) |
| Spot: David / Jesus / Moses / Ruth / Bigtha | 896 / 1,831 / 774 / 13 / 1 |
| person, relationship (Phase 1) | 3,050, 5,129 unchanged |

### Atlas (Cypher via `ExecuteCypherQuery`, domain `Bible-Project`)
- Nodes: Book 66, Chapter 1,189, Verse 31,102, Place 1,298, Folder 4 (3 from Phase 1 + `Bible.Places`)
- Edges: `mentions` 26,783 (19,249 to Person + 7,534 to Place), `writtenBy` 77, `partOf` 368, `sameAs` 257, `near` 19, `bornIn` 77, `diedIn` 45, `visited` 462, new `contains` 33,656 (66 + 1,189 + 31,102 + 1,298 + 1 for the Places folder)
- No Verse without a parent Chapter; no `mentions` edge with a missing target
- For 10 people (include David, Jesus, a one-verse person) and 5 places, count of incoming `mentions` = `VerseCount`
- Phase 1 counts unchanged (section 0, rule 3)
- Domain validation 0 errors

Save these queries as a script (`verify/phase2.cypher` + `verify/phase2.sql`) and re-run after every load.

## 9. Known limits (state them, don't fix them now)
- `mentions` = explicit name mentions as tagged by Theographic. Pronouns and titles ("the king") are not linked. Genealogy lists and narrative scenes look the same; a `MentionContext` property is a candidate for Phase 3.
- Verse years are Ussher-based and approximate; 3,078 verses have none.
- Theographic data issues found in Phase 1: merged Jezebel (Ahab's wife and Thyatira prophetess are one record), misattributed dictionary text for some people (corrected via overrides). Put any new corrections in override tables, never edit source rows.
- Place modern names/countries are empty. ModernCountry is politically sensitive: record the convention when you fill it.

## 10. After Phase 2 (planned order)
1. **Sections** (passages, e.g. "The Fall" Gen 3:1-24): start/end verse, link to verses
2. **Events**: Theographic has **450** events with dates and participants (not more). Event → `attestedIn` → Verse, role edges to Person, `occurredAt` → Place. Lets Phase 1 narrative edges point to evidence
3. **BSB text** (public domain): load into `verse_text` as translation `BSB`, plus BSB footnotes as Note nodes. Download from ebible.org (`engbsb`); verify 31,102 verses after versification mapping
4. **Cross-references**: OpenBible.info, ~340,000 links, CC BY 4.0, vote count as edge weight. Test compile scale on a branch first
5. **Original language**: STEPBible Data (CC BY 4.0) tagged Hebrew/Greek + lexicons. ~750,000 words: likely stays in Postgres, queried through Connect

## 11. Housekeeping
- Rotate the `Claude` Pulse client secret if not done already.
- Keep `HANDOFF.md` (Phase 1) and this file in the repo with the scripts.


## Phase 3: events (done 2026-10-29)

- Postgres: `migrations/05_events.sql` from `source/etl_events.py` (Theographic `events.json`; title fixes in
  `source/cur_events.py`). Tables `event` (450), `event_verse` (17,570), `event_participant` (881: 849 people,
  30 God / Holy Spirit, 2 Satan), `event_place` (476), `event_relation` (SubEventOf 202, Follows 392).
  Verify with `verify/phase3.sql` (12 checks). Apply after `04_phase2_adjustments.sql`.
- Atlas: library `bible-events` (Event; attestedIn, involves, occurredAt, subEventOf, follows), map file
  `events.map.json`, folder `Bible.Events`. Built on branch `phase3-events`, merged to main.
  main: 37,324 instances, 100,807 edges, validation 0 errors.
- **One conservative timeline** (Jeff's decision, 2026-10-29): `source/chronology.py` maps Theographic's Ussher-based
  years onto the conservative chronology (Reformation Study Bible: 430-year sojourn, Exodus 1446 BC, Saul 1050,
  David 1010, Solomon 970, temple 966, division 931, Thiele kings) by interpolating between 34 anchor events. Applied
  to events (`etl_events.py`), verse `approx_year` and source-dated person birth/death years (`gen_phase2_adjust.py`);
  curated person years are left alone. Before Abraham the Genesis genealogies are shifted with him (creation
  4174 BC, labelled as fixing no date); after 400 BC and in the New Testament source dates are kept. Every
  event and verse records which basis applies in `dating_basis`.
- Checked: 29 of 39 king records agree with their reign events within 3 years; of the rest, 3 are joins on a
  shared first name (Ahaziah, Joash, Jehoahaz) and 4 are co-regency conventions (Jehoram, Pekah, Jotham, Manasseh:
  the king record counts from the co-regency, the event from the sole reign).
- Source corrections: Lifetime of Jacob 147 years (Genesis 47:28; source had 180). Known source inconsistency left
  as is: Joshua's lifetime and death events disagree by 13 years.
- Item 5 curation also done: book summaries and composition dates (`source/cur_books.py`), place modern names and
  countries (`source/match_place_modern.py` -> `source/place_modern.tsv`, regions in `source/cur_place_modern.py`),
  verse links for divine manifestations (`records`).

## Trial: ESV text (added 2026-10-29)

- Separate table `bible.esv_text` (verse_id, text, status, note, edition, attribution) + view `v_atlas_esv_text`;
  nothing else in the database depends on it. Source: unofficial SQLite dump (github.com/BIBLE-Study/SQLite-Databases,
  `esv sqlite.sql`), which is the **2011 ESV text, not the 2016 permanent text** (Genesis 3:16 reads "for your
  husband"). Loaded by `source/gen_esv_trial.py` (patches in `source/cur_esv_patches.py`) into
  `migrations/90_esv_trial.sql`, which is **git-ignored: licensed text, never commit or publish it**.
- Statuses: 30,585 as imported; 500 typography fixed (`--` to em dash); 16 not in ESV text (the verses the ESV
  footnotes; empty text + note); 1 patched (3 John 14 now includes ESV verse 15, which the dump had lost).
- Atlas: `TextEsv` and `EsvNote` on Verse (bible-text), fed by a LEFT JOIN in the Connect `VersesDated/[Book]` and
  `VersesUndated/[Book]` queries.
- To remove: `DROP VIEW bible.v_atlas_esv_text; DROP TABLE bible.esv_text;` then take the join and the two columns out
  of those Connect queries, remove the TextEsv/EsvNote map entries from `verses-dated` / `verses-undated`, recompile.
