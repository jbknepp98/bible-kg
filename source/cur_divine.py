# God, the three divine persons, and their manifestations.
# Framework: Nicene (Trinitarian). One God (Godhead) in three persons (DivinePerson: Father, Son, Holy Spirit).
# A Manifestation is a distinct way a divine person (or God, where the text does not distinguish) appears in
# scripture: pre-existence, pre-incarnate appearances, the incarnation, resurrection appearances, exaltation,
# voices and visible signs. None of these are Persons or SpiritualBeings.
# identifiedWith links a manifestation to an existing node (Jesus of Nazareth, the Angel of the Lord, Melchizedek...)
# and records whether the identification is stated in the text or a traditional reading.
# Loaded by gen_divine.py -> initdb/05_divine.sql, which runs after 04_spirits.sql.
# All references were checked against the KJV text (Theographic verses.json).

GODHEAD = dict(id='god_1324', name='God', src='god_1324', vc=8587, ref='Genesis 1:1', both=True,
               aka='the LORD; JEHOVAH; the Almighty; the Most High; the Ancient of days',
               summary="The one God of Israel, creator of heaven and earth, revealed in three persons: the Father, the Son and the Holy Spirit. Theographic tags every verse that names God, the LORD, JEHOVAH, the Almighty or the Father to this record without distinguishing the persons, so those verse mentions attach here.")

PERSONS = [
 dict(id='god_the_father', name='God the Father', vc=0, ref='Matthew 3:17', both=True, aka='the Father; Abba',
      summary="First person of the Trinity. Speaks from heaven at Jesus' baptism and transfiguration, sends the Son and the Spirit, and is addressed by Jesus as 'Abba, Father'. Old Testament mentions of God are attached to God rather than to the Father, because the text does not distinguish the persons."),
 dict(id='god_the_son', name='God the Son', vc=0, ref='John 1:1', both=True, aka='the Word; the Son; Christ',
      summary="Second person of the Trinity: the eternal Word, who 'was with God, and was God', became flesh as Jesus of Nazareth, rose, ascended and reigns. His earthly life, relationships and verse mentions are on the Person 'Jesus of Nazareth'; this node ties together all his manifestations."),
 dict(id='holy_spirit_7400', name='Holy Spirit', src='holy_spirit_7400', vc=246, ref='Genesis 1:2', both=True,
      aka='Holy Ghost; the Spirit of God; the Comforter',
      summary="Third person of the Trinity. Moves upon the waters at creation, comes upon judges, kings and prophets, overshadows Mary, descends on Jesus at his baptism, and is poured out at Pentecost as the Comforter Jesus promised."),
]

# kind: Pre-existence, Pre-incarnate appearance, Incarnation, Resurrection appearance, Exaltation, Voice, Visible sign, Vision
MANIFESTATIONS = [
 # God the Son
 dict(id='word_in_the_beginning', name='The Word in the beginning', of='god_the_son', kind='Pre-existence', ref='John 1:1',
      passages=['John 1:1-3'],
      summary="The Word who was in the beginning with God and was God, through whom all things were made."),
 dict(id='christ_as_angel_of_the_lord', name='Christ as the Angel of the Lord', of='god_the_son', kind='Pre-incarnate appearance', ref='Genesis 16:7',
      passages=['Genesis 16:7-13', 'Exodus 3:2-6', 'Judges 13:18-22'],
      summary="The Angel of the Lord, who speaks as God and is worshipped as God (Hagar names him 'Thou God seest me'; he speaks from the bush as the God of Abraham; Manoah fears he has seen God). Traditionally read as an appearance of the pre-incarnate Son."),
 dict(id='christ_as_melchizedek', name='Christ as Melchizedek', of='god_the_son', kind='Pre-incarnate appearance', ref='Genesis 14:18',
      passages=['Genesis 14:18-20', 'Psalms 110:4', 'Hebrews 7:1-3'],
      summary="Melchizedek, king of Salem and priest of the most high God, who blessed Abraham; 'without father, without mother... made like unto the Son of God; abideth a priest continually'. Read here as an appearance of the Son."),
 dict(id='christ_wrestling_with_jacob', name='Christ wrestling with Jacob', of='god_the_son', kind='Pre-incarnate appearance', ref='Genesis 32:24',
      passages=['Genesis 32:24-30'],
      summary="The man who wrestled with Jacob at Peniel and blessed him; Jacob said 'I have seen God face to face'. Traditionally read as an appearance of the pre-incarnate Son."),
 dict(id='christ_as_captain_of_the_host', name="Christ as captain of the LORD's host", of='god_the_son', kind='Pre-incarnate appearance', ref='Joshua 5:13',
      passages=['Joshua 5:13-15'],
      summary="The captain of the LORD's host who appeared to Joshua with a drawn sword, accepted his worship and declared the ground holy. Traditionally read as an appearance of the pre-incarnate Son."),
 dict(id='christ_in_the_furnace', name='Christ in the fiery furnace', of='god_the_son', kind='Pre-incarnate appearance', ref='Daniel 3:25',
      passages=['Daniel 3:24-28'],
      summary="The fourth man in the furnace whose form was 'like the Son of God'. Traditionally read as an appearance of the pre-incarnate Son; Nebuchadnezzar calls him God's angel."),
 dict(id='incarnation_of_the_son', name='Incarnation of the Son', of='god_the_son', kind='Incarnation', ref='John 1:14',
      passages=['John 1:14', 'Matthew 1:23', 'Luke 2:7-11', 'Philippians 2:6-8'],
      summary="'The Word was made flesh, and dwelt among us': the Son born of Mary as Jesus of Nazareth, Emmanuel, God with us."),
 dict(id='risen_christ', name='Risen Christ', of='god_the_son', kind='Resurrection appearance', ref='Matthew 28:9',
      passages=['Matthew 28:9-10', 'Matthew 28:16-20', 'Luke 24:13-51', 'John 20:11-29', 'John 21:1-23', 'Acts 1:3-9', '1 Corinthians 15:5-8'],
      summary="Jesus raised bodily from the dead, appearing over forty days to Mary Magdalene, the women, the disciples on the Emmaus road, Thomas, Peter, James and more than five hundred at once, before ascending from the Mount of Olives."),
 dict(id='exalted_christ', name='Exalted Christ', of='god_the_son', kind='Exaltation', ref='Acts 7:55',
      aka='one like unto the Son of man; the Lamb', passages=['Acts 7:55-56', 'Acts 9:3-6', 'Revelation 1:13-18', 'Revelation 5:6'],
      summary="The ascended Christ at the right hand of God: seen by Stephen standing at God's right hand, revealed to Saul on the Damascus road, and seen by John as one like the Son of man among the lampstands and as the Lamb that was slain."),
 # God the Father
 dict(id='voice_at_the_baptism', name='Voice from heaven at the baptism', of='god_the_father', kind='Voice', ref='Matthew 3:17',
      passages=['Matthew 3:17', 'Mark 1:11', 'Luke 3:22'],
      summary="The Father's voice at Jesus' baptism: 'This is my beloved Son, in whom I am well pleased.'"),
 dict(id='voice_at_the_transfiguration', name='Voice from the cloud at the transfiguration', of='god_the_father', kind='Voice', ref='Matthew 17:5',
      passages=['Matthew 17:5', 'Mark 9:7', 'Luke 9:35', '2 Peter 1:17-18'],
      summary="The Father's voice from the bright cloud on the mount: 'This is my beloved Son, in whom I am well pleased; hear ye him.'"),
 dict(id='ancient_of_days', name='The Ancient of days', of='god_the_father', kind='Vision', ref='Daniel 7:9',
      passages=['Daniel 7:9-10', 'Daniel 7:13', 'Daniel 7:22'],
      summary="The Ancient of days seen enthroned in Daniel's vision, with raiment white as snow, to whom one like the Son of man is brought and given dominion. Traditionally identified with the Father."),
 # God (the text does not distinguish the person)
 dict(id='pillar_of_cloud_and_fire', name='Pillar of cloud and of fire', of='god_1324', kind='Visible sign', ref='Exodus 13:21',
      passages=['Exodus 13:21-22', 'Exodus 14:19-20', 'Exodus 14:24', 'Exodus 33:9-10'],
      summary="The LORD going before Israel by day in a pillar of cloud and by night in a pillar of fire, and standing between Israel and the Egyptians at the Red Sea."),
 dict(id='fire_on_sinai', name='Fire and cloud on Mount Sinai', of='god_1324', kind='Visible sign', ref='Exodus 19:18',
      passages=['Exodus 19:16-20', 'Exodus 24:16-17'],
      summary="The LORD descending on Mount Sinai in fire, smoke and thick cloud, with thunder and the sound of the trumpet, when he gave the Law."),
 # Holy Spirit
 dict(id='spirit_as_a_dove', name='Spirit descending like a dove', of='holy_spirit_7400', kind='Visible sign', ref='Matthew 3:16',
      passages=['Matthew 3:16', 'Mark 1:10', 'Luke 3:22', 'John 1:32-33'],
      summary="The Spirit of God descending like a dove and lighting on Jesus at his baptism, the sign by which John the Baptist knew him."),
 dict(id='tongues_of_fire', name='Cloven tongues of fire at Pentecost', of='holy_spirit_7400', kind='Visible sign', ref='Acts 2:3',
      passages=['Acts 2:1-4'],
      summary="The rushing mighty wind and cloven tongues like as of fire that sat on each of the disciples at Pentecost, when they were all filled with the Holy Ghost."),
]

# (from, type, to, scripture_reference, interpretation). interpretation only applies to IdentifiedWith.
RELS = [
 ('god_the_father', 'PersonOf', 'god_1324', '1 Corinthians 8:6', None),
 ('god_the_son', 'PersonOf', 'god_1324', 'John 1:1', None),
 ('holy_spirit_7400', 'PersonOf', 'god_1324', 'Matthew 28:19', None),
 # identifications with existing nodes
 ('incarnation_of_the_son', 'IdentifiedWith', 'jesus_905', 'John 1:14', 'Explicit in text'),
 ('christ_as_angel_of_the_lord', 'IdentifiedWith', 'angel_of_the_lord_9101', 'Genesis 16:13', 'Traditional, debated'),
 ('christ_as_melchizedek', 'IdentifiedWith', 'melchisedec_1991', 'Hebrews 7:3', 'Traditional, debated'),
 ('christ_wrestling_with_jacob', 'IdentifiedWith', 'man_who_wrestled_jacob_9102', 'Genesis 32:30', 'Traditional, debated'),
 ('christ_as_captain_of_the_host', 'IdentifiedWith', 'captain_of_the_host_9118', 'Joshua 5:14', 'Traditional, debated'),
 ('christ_in_the_furnace', 'IdentifiedWith', 'fourth_man_in_the_furnace_9105', 'Daniel 3:25', 'Traditional, debated'),
 ('exalted_christ', 'IdentifiedWith', 'jesus_905', 'Acts 9:5', 'Explicit in text'),
 ('risen_christ', 'IdentifiedWith', 'jesus_905', 'Luke 24:39', 'Explicit in text'),
 # appearances
 ('risen_christ', 'AppearedTo', 'mary_1943', 'John 20:14', None),
 ('risen_christ', 'AppearedTo', 'cleophas_950', 'Luke 24:18', None),
 ('risen_christ', 'AppearedTo', 'thomas_2851', 'John 20:26', None),
 ('risen_christ', 'AppearedTo', 'peter_2745', '1 Corinthians 15:5', None),
 ('risen_christ', 'AppearedTo', 'james_719', '1 Corinthians 15:7', None),
 ('exalted_christ', 'AppearedTo', 'stephen_2802', 'Acts 7:56', None),
 ('exalted_christ', 'AppearedTo', 'paul_2479', 'Acts 9:5', None),
 ('exalted_christ', 'AppearedTo', 'john_1677', 'Revelation 1:17', None),
 ('ancient_of_days', 'AppearedTo', 'daniel_975', 'Daniel 7:9', None),
 ('pillar_of_cloud_and_fire', 'AppearedTo', 'moses_2108', 'Exodus 33:9', None),
 ('fire_on_sinai', 'AppearedTo', 'moses_2108', 'Exodus 19:20', None),
 ('spirit_as_a_dove', 'AppearedTo', 'john_1676', 'John 1:32', None),
 ('voice_at_the_baptism', 'AnnouncedTo', 'jesus_905', 'Mark 1:11', None),
 ('voice_at_the_transfiguration', 'AnnouncedTo', 'peter_2745', 'Matthew 17:5', None),
 ('voice_at_the_transfiguration', 'AnnouncedTo', 'james_717', 'Matthew 17:5', None),
 ('voice_at_the_transfiguration', 'AnnouncedTo', 'john_1677', 'Matthew 17:5', None),
]

NEW_TYPES = [
 ('PersonOf', 'Divine', 'Subject is one of the three persons of the one God (the object).'),
 ('ManifestationOf', 'Divine', 'Subject is a manifestation (appearance, voice, sign or state) of the object.'),
 ('IdentifiedWith', 'Divine', 'Subject manifestation is identified with the object node; interpretation records whether the text states it or tradition reads it so.'),
]
