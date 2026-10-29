// Phase 2 verification (Atlas, domain Bible-Project). Run each query with ExecuteCypherQuery after every compile.
// Expected values as of 2026-10-29 are in the comments. Written for the Atlas Cypher engine (no pattern
// predicates in WHERE, no count() inside CASE).

// 1. Node counts by type. Expect: Verse 31102, Place 1298, Chapter 1189, Book 66, Folder 6,
//    Person 2862, King 141, Prophet 62, Priest 34, Judge 14, Apostle 19,
//    FalseGod 26, Angel 21, Demon 8, SpiritualBeing 3, Principality 2, Manifestation 16, DivinePerson 3, Godhead 1
MATCH (n) WITH labels(n)[0] AS type, count(*) AS n WHERE NOT type ENDS WITH 'StrategyNode' AND NOT type CONTAINS ':' + 'x'
RETURN type, n ORDER BY n DESC;

// 2. Phase 2 edges by type and target. Expect mentions: Person-family 20366 (Person 11548, Prophet 3854, King 3518,
//    Priest 740, Apostle 549, Judge 157), Place 7534, Godhead 8587, DivinePerson 246, beings 402
//    (Angel 165, FalseGod 119, SpiritualBeing 68, Demon 47, Principality 3); writtenBy 77; partOf 368; sameAs 257;
//    near 19; bornIn 77; diedIn 45; visited 462; contains to Verse 31102, Chapter 1189, Book 66, Place 1298
MATCH ()-[r]->(t) WITH type(r) AS rel, labels(t)[0] AS target, count(*) AS n
WHERE rel ENDS WITH ':mentions' OR rel ENDS WITH ':writtenBy' OR rel ENDS WITH ':partOf' OR rel ENDS WITH ':near'
   OR rel ENDS WITH ':sameAs' OR rel ENDS WITH ':bornIn' OR rel ENDS WITH ':diedIn' OR rel ENDS WITH ':visited'
   OR rel ENDS WITH ':contains'
RETURN rel, target, n ORDER BY rel, n DESC;

// 3. Every verse has a parent chapter. Expect 31102
MATCH (c:`urn:atlas:ontology:bible-text:Chapter`)-[:`urn:atlas:ontology:atlas-common:contains`]->(v:`urn:atlas:ontology:bible-text:Verse`)
RETURN count(DISTINCT v) AS versesWithAChapter;

// 4. Incoming mentions = VerseCount for a sample of people, beings, God and places (every row: verseCount = mentions)
MATCH (v)-[m:`urn:atlas:ontology:bible-text:mentions`]->(t)
WHERE t.Uri IN ['Bible.Person.david_994','Bible.Person.jesus_905','Bible.Person.moses_2108','Bible.Person.ruth_2450',
                'Bible.Person.bigtha_494','Bible.Person.mary_1943','Bible.Person.paul_2479','Bible.Person.gerasene_demoniac_9001',
                'Bible.Person.mary_1942','Bible.Person.abraham_58','Bible.Spirit.satan_2476','Bible.Spirit.legion_9120',
                'Bible.Divine.god_1324','Bible.Divine.holy_spirit_7400','Bible.Place.jerusalem_636','Bible.Place.bethlehem_218',
                'Bible.Place.ramah_975','Bible.Place.babylon_151','Bible.Place.ophrah_914']
RETURN t.DisplayName AS name, t.VerseCount AS verseCount, count(m) AS mentions ORDER BY mentions DESC;

// 5. Phase 1 relationships unchanged. Expect siblingOf 2331, begot 1795, halfSiblingOf 244, married 119, ...
MATCH ()-[r]->() WITH type(r) AS rel, count(*) AS n WHERE rel STARTS WITH 'urn:atlas:ontology:bible-people:'
RETURN rel, n ORDER BY n DESC;
