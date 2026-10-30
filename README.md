# bible-kg

A knowledge graph of the Bible: every named person, the unnamed people who act in the narratives, spiritual beings,
God and the persons of the Trinity, books, chapters, verses (KJV, BSB, ESV, NET, with footnotes) and places, with family, narrative and
mention relationships. It is served from PostgreSQL through Timebase Connect into a Timebase Atlas domain
(`Bible-Project`, libraries `bible-people`, `bible-places`, `bible-text`).

## Layout

| Path | What it is |
|---|---|
| `initdb/` | Builds a fresh database in a `postgres:16` container (people, relationships, unnamed people, spiritual beings, divine model). `99_reader_password.sh` sets the Connect login's password from `bible.env` |
| `migrations/` | Applied to an existing database: Phase 2 text and places (`03`), project adjustments (`04`), events (`05`), translations and footnotes (`06`). `91_licensed_translations.sql` (ESV, NET) is generated locally and never committed |
| `source/` | Generators and the curated data they read (`cur_*.py`). Edit the curated file, run its `gen_*.py`, re-apply the SQL |
| `verify/` | Re-runnable checks: `phase2.sql`, `phase3.sql`, `translations.sql` (Postgres) and `phase2.cypher` (Atlas) |
| `HANDOFF.md`, `HANDOFF-PHASE2.md` | Build notes and current status |

`bible.env` (database passwords) is not in the repository. Create it locally with `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `TIMEBASE_READER_USER` and `TIMEBASE_READER_PASSWORD`.

```bash
docker run -d --name bible-pg --env-file bible.env -p 5433:5432 \
  -v "$PWD/initdb":/docker-entrypoint-initdb.d:ro -v bible-pg-data:/var/lib/postgresql/data postgres:16
docker exec -i bible-pg psql -U bible_admin -d bible -v ON_ERROR_STOP=1 < migrations/03_text_places.sql
docker exec -i bible-pg psql -U bible_admin -d bible -v ON_ERROR_STOP=1 < migrations/04_phase2_adjustments.sql
docker exec -i bible-pg psql -U bible_admin -d bible < verify/phase2.sql
docker exec -i bible-pg psql -U bible_admin -d bible -v ON_ERROR_STOP=1 < migrations/05_events.sql
docker exec -i bible-pg psql -U bible_admin -d bible -v ON_ERROR_STOP=1 < migrations/06_translations.sql
# licensed text, generated locally by source/gen_translations.py:
docker exec -i bible-pg psql -U bible_admin -d bible -v ON_ERROR_STOP=1 < migrations/91_licensed_translations.sql
```

## Conventions

- Display names never use parentheses or scripture references. Ambiguous names get a qualifier from scripture:
  an epithet ("Ahijah the Shilonite"), a title ("Omri, king of Israel"), a relationship ("Mary, wife of Cleophas"),
  or a role in the list where the person appears. The reference stays in `first_reference`.
- God and the Holy Spirit are not spiritual beings. The divine model is Nicene (one God in three persons), with
  manifestations such as the Incarnation and the pre-incarnate appearances of the Son. Identifications that
  scripture does not state outright are marked `Traditional, debated`.
- Theological curation follows a conservative, Reformed evangelical reading.

## Sources and licence

- **Theographic Bible Metadata** by Robert Rouse, https://github.com/robertrouse/theographic-bible-metadata,
  licensed **CC BY-SA 4.0**. People, places, verses and their links are derived from it, so the data in this
  repository (`initdb/`, `migrations/`) is shared under **CC BY-SA 4.0** as well.
- **King James Version** text: public domain.
- **Berean Standard Bible** (BSB) text and footnotes: public domain ("This text of God's Word has been dedicated to the
  public domain"), from the ebible.org USFM edition `engbsb`. The verse-citation links are derived from its footnotes.
- **English Standard Version** (ESV) and **NET Bible** text are used by permission and are **not** in this
  repository. ESV: Scripture quotations are from the ESV® Bible, © 2001 by Crossway, used by permission.
  NET: Scripture quoted by permission. Quotations designated (NET) are from the NET Bible® copyright ©1996, 2019 by
  Biblical Studies Press, L.L.C. http://netbible.com All rights reserved. Only the import code and small
  corrections (`source/esv_import.py`, `source/cur_esv_patches.py`) are kept here.
- **Easton's Bible Dictionary** (1897, public domain), via Theographic, for many summaries.
- **OpenBible.info Bible Geocoding Data**, https://github.com/openbibleinfo/Bible-Geocoding-Data, **CC BY 4.0**:
  modern site identifications for places (`source/match_place_modern.py`, only identifications OpenBible rates
  with confidence >= 500 and within 15 km).
- **Natural Earth** admin-0 country boundaries (public domain) for place countries. Convention: every site west of
  the Jordan, including Jerusalem, the West Bank and Gaza, is recorded as Israel.
- Book summaries and composition dates are curated from a conservative Reformed evangelical position (Ligonier
  Ministries, the Reformation Study Bible); contested dates are given as ranges with the views named.
- Curated additions (unnamed people, spiritual beings, divine model, display-name epithets, narrative edges) were
  written for this project and checked against the KJV text. They are released under the same CC BY-SA 4.0 terms.
