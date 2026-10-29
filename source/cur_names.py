# Display names for people whose generated name ended in a scripture reference (e.g. "Mary, Romans 16:6").
# gen_names.py resolves each such person with the first rule that gives a unique name:
#   1. OVERRIDES            hand-written epithet, usually the KJV's own ("Ahijah the Shilonite")
#   2. role tables          "Omri, king of Israel", "Gad the prophet", "Urijah the priest"
#   3. family               spouse, child, parent, sibling: "Mary, wife of Cleophas"
#   4. VERSE_ROLES          role in the list the person appears in: "Uriel, chief of the sons of Kohath"
#   5. CLANS                clan named in the list verse, when two would otherwise collide: "Maaseiah, of the sons of Harim"
#   6. ordinal              ", first" / ", second" in verse order, for the few scripture itself cannot separate
# Names never use parentheses and never contain a scripture reference; the reference stays in first_reference.
# Every epithet and role here was written against the KJV text of the person's first reference.
# OVERRIDES keys are a person_id or 'First reference|First name' (the latter cannot silently hit the wrong person).

OVERRIDES = {
 # prophets, priests, officials and foreigners known by a title
 'ahijah_135': 'Ahijah the Shilonite', 'shemaiah_2619': 'Shemaiah the man of God', 'gad_1263': 'Gad the seer',
 'iddo_1594': 'Iddo the seer', 'amos_238': 'Amos the prophet', 'obadiah_2226': 'Obadiah the prophet',
 'micah_2053': 'Micah the Morasthite', 'micah_2049': 'Micah of mount Ephraim', 'noadiah_2209': 'Noadiah the prophetess',
 'shemaiah_2643': 'Shemaiah the Nehelamite', 'oded_2237': 'Oded the prophet',
 'amariah_201': 'Amariah the chief priest', 'urijah_2903': 'Urijah the priest', 'mattan_1948': 'Mattan, priest of Baal',
 'amaziah_217': 'Amaziah, priest of Bethel', 'jehoiada_796': "Jehoiada, priest before Zephaniah",
 'pashur_2285': 'Pashur, chief governor of the temple', 'ananias_260': 'Ananias the high priest',
 'Nehemiah 3:1|Eliashib': 'Eliashib the high priest',
 'obadiah_2215': "Obadiah, governor of Ahab's house", 'amon_235': 'Amon, governor of Samaria',
 'joshua_1729': 'Joshua, governor of Jerusalem', 'shebna_2577': 'Shebna the scribe', 'shebna_2578': 'Shebna the treasurer',
 'elishama_1160': 'Elishama the scribe', 'jonathan_1701': 'Jonathan the scribe', 'hananiah_1391': 'Hananiah, ruler of the palace',
 'asaph_332': "Asaph, keeper of the king's forest", 'mithredath_2097': 'Mithredath the treasurer',
 'arioch_304': "Arioch, captain of the king's guard", 'tarshish_2829': 'Tarshish, prince of Persia',
 'uzza_2912': 'Uzza, owner of the royal garden', 'hiram_1533': 'Hiram, craftsman of Tyre', 'cushi_964': "Cushi, Joab's messenger",
 'ira_608': 'Ira the Jairite', 'ittai_656': 'Ittai the Gittite', 'barzillai_411': 'Barzillai the Gileadite',
 'ahimelech_148': 'Ahimelech the Hittite', 'joshua_1728': 'Joshua the Bethshemite', 'zerah_3046': 'Zerah the Ethiopian',
 'nahash_2136': 'Nahash the Ammonite', 'naaman_2122': 'Naaman the Syrian', 'eliphaz_1145': 'Eliphaz the Temanite',
 'eliezer_1113': 'Eliezer of Damascus', 'deborah_996': "Deborah, Rebekah's nurse", 'puah_2372': 'Puah the midwife',
 'gog_1326': 'Gog of Magog', 'ram_2393': 'Ram, ancestor of Elihu', 'ithiel_651': 'Ithiel, to whom Agur spoke',
 'henadad_1493': 'Henadad, head of a Levite family', 'bedan_427': 'Bedan, deliverer of Israel',
 'jair_709': 'Jair the Gileadite', 'elon_1184': 'Elon the Zebulonite',
 # kings named outside the king table
 'agag_109': 'Agag, king of the Amalekites', 'agag_108': "Agag of Balaam's oracle", 'mesha_2009': 'Mesha, king of Moab',
 'abimelech_40': 'Abimelech, king of Gerar', 'arioch_303': 'Arioch, king of Ellasar', 'japhia_727': 'Japhia, king of Lachish',
 'jabin_676': 'Jabin, king of Hazor', 'jabin_677': 'Jabin, king of Canaan', 'jobab_1642': 'Jobab, king of Madon',
 'ben-hadad_453': 'Ben-hadad, besieger of Samaria', 'pharaoh_2333': 'Pharaoh in the days of Hezekiah',
 'pharaoh_2335': "Pharaoh of Jeremiah's prophecy", 'pharaoh_2336': 'Pharaoh Hophra',
 'Numbers 31:8|Rekem': 'Rekem, king of Midian', 'Numbers 31:8|Zur': 'Zur, king of Midian', 'Numbers 31:8|Hur': 'Hur, king of Midian',
 # New Testament
 'Acts 9:10|Ananias': 'Ananias of Damascus', 'Acts 9:11|Judas': 'Judas of Straight Street', 'Acts 9:43|Simon': 'Simon the tanner',
 'simon_2752': 'Simon the sorcerer', 'simon_2748': 'Simon the leper', 'simeon_2742': 'Simeon of Jerusalem',
 'simeon_2744': 'Simeon called Niger', 'judas_1759': 'Judas called Barsabas', 'judas_1757': 'Judas of Galilee',
 'jesus_904': 'Jesus called Justus', 'mary_1942': 'Mary of Rome', 'Romans 16:13|Rufus': 'Rufus, chosen in the Lord',
 'Romans 16:23|Gaius': "Gaius, Paul's host", 'gaius_1272': 'Gaius, beloved of John', 'gaius_1269': 'Gaius of Macedonia',
 'gaius_1270': 'Gaius of Derbe', 'alexander_187': 'Alexander, kinsman of the high priest',
 'john_1678': 'John, kinsman of the high priest', 'alexander_188': 'Alexander of the Ephesian riot',
 'alexander_189': 'Alexander, companion of Hymenaeus',
 # people from lists whose verse gives a specific title
 'Ezra 10:15|Shabbethai': 'Shabbethai the Levite', 'Ezra 10:15|Meshullam': 'Meshullam, helper in the foreign-marriage inquiry',
 'Nehemiah 12:22|Darius': 'Darius the Persian', 'Ezra 4:7|Artaxerxes': 'Artaxerxes, king of Persia',
 'artaxerxes_314': 'Artaxerxes of the temple decree', 'Ezra 4:7|Mithredath': 'Mithredath, writer against Jerusalem',
 'Ezra 4:8|Rehum': 'Rehum the chancellor', 'Nehemiah 13:13|Zadok': 'Zadok the scribe', 'Nehemiah 13:13|Shelemiah': 'Shelemiah the priest',
 'Nehemiah 13:13|Pedaiah': 'Pedaiah, Levite treasurer', 'Nehemiah 13:4|Eliashib': 'Eliashib, priest allied to Tobiah',
 'Nehemiah 11:14|Zabdiel': 'Zabdiel, overseer of the mighty men', 'Nehemiah 11:21|Ziha': 'Ziha, over the Nethinims',
 '1 Chronicles 12:18|Amasai': 'Amasai, chief of the captains', 'Ezra 8:17|Iddo': 'Iddo, chief at Casiphia',
 'Ezra 8:18|Sherebiah': 'Sherebiah, man of understanding', '1 Chronicles 15:22|Chenaniah': 'Chenaniah, chief of the Levites in song',
 'elkanah_1173': 'Elkanah, doorkeeper for the ark', '2 Chronicles 31:10|Azariah': 'Azariah, chief priest under Hezekiah',
 '2 Chronicles 26:17|Azariah': 'Azariah, priest who withstood Uzziah', '2 Chronicles 26:5|Zechariah': 'Zechariah, counsellor of Uzziah',
 '2 Chronicles 28:7|Zichri': 'Zichri, mighty man of Ephraim', '2 Chronicles 28:7|Azrikam': 'Azrikam, governor of the house of Ahaz',
 '2 Chronicles 34:8|Maaseiah': 'Maaseiah, governor of Jerusalem', '1 Chronicles 9:5|Asaiah': 'Asaiah, firstborn of the Shilonites',
 'Genesis 36:37|Shaul': 'Shaul of Rehoboth', '1 Chronicles 27:4|Mikloth': "Mikloth, ruler in Dodai's course",
 '1 Chronicles 27:27|Shimei': 'Shimei the Ramathite', '1 Chronicles 27:27|Zabdi': 'Zabdi the Shiphmite', 'baal-hanan_577': 'Baal-hanan the Gederite',
 'joash_1637': "Joash, over David's cellars of oil",
 'sisera_2757': "Sisera, captain of Jabin's host", 'shuah_2728': 'Shuah the Canaanite',
 'abinadab_45': "Abinadab, father of Solomon's governor in Dor", 'hur_1573': "Hur, father of Solomon's governor in mount Ephraim",
 'geber_1285': "Geber, father of Solomon's governor in Ramoth-gilead", 'elkanah_1174': 'Elkanah, next to King Ahaz',
 '1 Chronicles 27:30|Jehdeiah': 'Jehdeiah the Meronothite',
 '2 Chronicles 17:14|Adnah': 'Adnah, captain of thousands of Judah', '2 Chronicles 17:17|Eliada': 'Eliada, mighty man of Benjamin',
 'Nehemiah 3:17|Hashabiah': 'Hashabiah, ruler of half of Keilah', 'Nehemiah 3:13|Hanun': 'Hanun, repairer of the valley gate',
 'Nehemiah 3:31|Malchiah': "Malchiah, goldsmith's son", 'Nehemiah 3:8|Hananiah': 'Hananiah the apothecary',
 '1 Chronicles 26:16|Shuppim': 'Shuppim, gatekeeper of the west gate', '1 Chronicles 26:20|Ahijah': 'Ahijah, over the temple treasures',
 '1 Chronicles 26:29|Chenaniah': 'Chenaniah, Izharite officer and judge', '1 Chronicles 26:30|Hashabiah': 'Hashabiah, Hebronite officer',
 'azariah_543': 'Azariah, leader who returned with Zerubbabel', 'jedaiah_756': 'Jedaiah, returned from Babylon',
 'tobijah_2874': 'Tobijah, returned from Babylon', 'jahaziel_697': 'Jahaziel, priest with trumpets before the ark',
 'Ezra 4:5|Darius': 'Darius, king of Persia',
 # Ezra 8:16 names three Elnathans: two among the chief men, one among the men of understanding (verse order = id order)
 'elnathan_1178': 'Elnathan, chief man sent by Ezra, first', 'elnathan_1179': 'Elnathan, chief man sent by Ezra, second',
 'elnathan_1180': 'Elnathan, man of understanding sent by Ezra',
 'daughter_of_pharaoh_989': 'Daughter of Pharaoh, wife of Solomon',
}

# Mighty men lists in 2 Samuel 23 / 1 Chronicles 11 and similar give a gentilic straight after the name:
# "Shammah the Harodite". Keyed by first reference; the name is taken from the person's first_name.
GENTILIC = {
 '2 Samuel 23:25': 'the Harodite', '2 Samuel 23:26': 'the Paltite', '2 Samuel 23:27': 'the Anethothite',
 '2 Samuel 23:30': 'the Pirathonite', '2 Samuel 23:31': 'the Barhumite', '2 Samuel 23:36': 'the Gadite',
 '2 Samuel 23:38': 'the Ithrite', '1 Chronicles 11:32': 'the Arbathite', '1 Chronicles 12:3': 'the Antothite',
 '1 Chronicles 11:46': 'the Mahavite',
}
# 1 Chronicles 11:36 has two gentilics in one verse
GENTILIC_BY_NAME = {('1 Chronicles 11:36', 'Hepher'): 'the Mecherathite', ('1 Chronicles 11:36', 'Ahijah'): 'the Pelonite',
                    ('1 Chronicles 12:5', 'Shephatiah'): 'the Haruphite'}

# (book chapter, first verse, last verse, role). The role follows "Name, ".
VERSE_ROLES = [
 ('Ezra 10', 18, 22, 'priest who married a foreign wife'), ('Ezra 10', 23, 23, 'Levite who married a foreign wife'),
 ('Ezra 10', 24, 24, 'temple servant who married a foreign wife'), ('Ezra 10', 25, 43, 'who married a foreign wife'),
 ('Nehemiah 10', 2, 8, 'priest who sealed the covenant'), ('Nehemiah 10', 9, 13, 'Levite who sealed the covenant'),
 ('Nehemiah 10', 14, 27, 'chief who sealed the covenant'),
 ('Nehemiah 12', 1, 7, 'priest who returned with Zerubbabel'), ('Nehemiah 12', 8, 9, 'Levite who returned with Zerubbabel'),
 ('Nehemiah 12', 25, 25, 'gatekeeper in the days of Joiakim'), ('Nehemiah 12', 32, 34, 'leader at the wall dedication'),
 ('Nehemiah 12', 41, 41, 'priest with trumpets at the wall dedication'), ('Nehemiah 12', 42, 42, 'singer at the wall dedication'),
 ('Ezra 2', 2, 2, 'leader who returned with Zerubbabel'), ('Ezra 2', 3, 35, 'ancestral head of returning exiles'),
 ('Ezra 2', 42, 42, 'ancestral head of returning porters'), ('Ezra 2', 43, 54, 'ancestral head of returning temple servants'),
 ('Ezra 2', 55, 58, "ancestral head of Solomon's servants"), ('Ezra 2', 59, 60, 'ancestral head of returnees of unproven descent'),
 ('Ezra 2', 61, 62, 'ancestral head of priests of unproven descent'),
 ('1 Chronicles 12', 3, 7, 'Benjamite who joined David at Ziklag'),
 ('1 Chronicles 12', 20, 20, 'captain of Manasseh who joined David'),
 ('Ezra 8', 2, 14, 'who returned with Ezra'), ('Ezra 8', 16, 16, 'chief man sent by Ezra'),
 ('Ezra 8', 19, 19, 'Merarite who returned with Ezra'),
 ('Nehemiah 8', 4, 4, 'who stood with Ezra at the reading of the Law'), ('Nehemiah 8', 7, 7, 'Levite who taught the Law'),
 ('1 Chronicles 15', 18, 18, 'Levite singer of the second degree'), ('1 Chronicles 15', 21, 21, 'harpist before the ark'),
 ('1 Chronicles 15', 24, 24, 'priest with trumpets before the ark'),
 ('2 Chronicles 17', 7, 7, 'prince sent to teach in Judah'), ('2 Chronicles 17', 8, 8, 'Levite sent to teach in Judah'),
 ('2 Chronicles 17', 15, 18, 'captain under Jehoshaphat'),
 ('2 Chronicles 31', 13, 13, 'overseer of the offerings under Hezekiah'),
 ('2 Chronicles 31', 15, 15, 'distributor of the offerings under Hezekiah'),
 ('1 Chronicles 5', 7, 7, 'chief of Reuben'), ('1 Chronicles 5', 12, 12, 'chief of Gad in Bashan'),
 ('1 Chronicles 5', 24, 24, 'head of a house of eastern Manasseh'),
 ('2 Chronicles 29', 12, 14, 'Levite who cleansed the temple under Hezekiah'),
 ('Nehemiah 3', 23, 23, 'repairer of the wall'),
 ('2 Chronicles 35', 8, 8, 'ruler of the house of God under Josiah'), ('2 Chronicles 35', 9, 9, 'chief of the Levites under Josiah'),
 ('1 Chronicles 11', 47, 47, "one of David's mighty men"),
 ('1 Chronicles 4', 35, 36, 'prince of Simeon'),
 ('1 Chronicles 9', 10, 10, 'priest who settled in Jerusalem'), ('1 Chronicles 9', 15, 15, 'Levite who settled in Jerusalem'),
 ('1 Chronicles 9', 17, 17, 'gatekeeper who settled in Jerusalem'),
 ('Genesis 36', 40, 43, 'duke of Edom'),
 ('2 Chronicles 26', 11, 11, "officer of Uzziah's army"),
 ('2 Chronicles 28', 12, 12, 'head of Ephraim'),
 ('Nehemiah 9', 4, 5, 'Levite who led the confession'),
 ('2 Chronicles 34', 12, 12, 'overseer of the temple repairs under Josiah'),
 ('Nehemiah 11', 16, 16, 'chief Levite over the outward business'),
]

# Ranked lists: the verse gives each person's position.
RANKED = {
 # 1 Chronicles 12:9-13, Gadite captains who joined David
 ('1 Chronicles 12:9', 'Ezer'): 'Ezer, first of the Gadite captains', ('1 Chronicles 12:9', 'Obadiah'): 'Obadiah, second of the Gadite captains',
 ('1 Chronicles 12:9', 'Eliab'): 'Eliab, third of the Gadite captains', ('1 Chronicles 12:10', 'Jeremiah'): 'Jeremiah, fifth of the Gadite captains',
 ('1 Chronicles 12:11', 'Attai'): 'Attai, sixth of the Gadite captains', ('1 Chronicles 12:11', 'Eliel'): 'Eliel, seventh of the Gadite captains',
 ('1 Chronicles 12:12', 'Johanan'): 'Johanan, eighth of the Gadite captains', ('1 Chronicles 12:12', 'Elzabad'): 'Elzabad, ninth of the Gadite captains',
 ('1 Chronicles 12:13', 'Jeremiah'): 'Jeremiah, tenth of the Gadite captains',
 # 1 Chronicles 24, the twenty-four priestly courses
 ('1 Chronicles 24:7', 'Jedaiah'): 'Jedaiah, head of the second priestly course', ('1 Chronicles 24:8', 'Harim'): 'Harim, head of the third priestly course',
 ('1 Chronicles 24:9', 'Malchijah'): 'Malchijah, head of the fifth priestly course', ('1 Chronicles 24:10', 'Abijah'): 'Abijah, head of the eighth priestly course',
 ('1 Chronicles 24:11', 'Shecaniah'): 'Shecaniah, head of the tenth priestly course', ('1 Chronicles 24:12', 'Eliashib'): 'Eliashib, head of the eleventh priestly course',
 ('1 Chronicles 24:12', 'Jakim'): 'Jakim, head of the twelfth priestly course', ('1 Chronicles 24:14', 'Bilgah'): 'Bilgah, head of the fifteenth priestly course',
 ('1 Chronicles 24:14', 'Immer'): 'Immer, head of the sixteenth priestly course', ('1 Chronicles 24:15', 'Hezir'): 'Hezir, head of the seventeenth priestly course',
 ('1 Chronicles 24:16', 'Pethahiah'): 'Pethahiah, head of the nineteenth priestly course', ('1 Chronicles 24:17', 'Jachin'): 'Jachin, head of the twenty-first priestly course',
 ('1 Chronicles 24:18', 'Delaiah'): 'Delaiah, head of the twenty-third priestly course',
 # 1 Chronicles 15:5-10, chiefs of the Levite families who carried the ark
 ('1 Chronicles 15:5', 'Uriel'): 'Uriel, chief of the sons of Kohath', ('1 Chronicles 15:6', 'Asaiah'): 'Asaiah, chief of the sons of Merari',
 ('1 Chronicles 15:7', 'Joel'): 'Joel, chief of the sons of Gershom', ('1 Chronicles 15:8', 'Shemaiah'): 'Shemaiah, chief of the sons of Elizaphan',
 ('1 Chronicles 15:9', 'Eliel'): 'Eliel, chief of the sons of Hebron', ('1 Chronicles 15:10', 'Amminadab'): 'Amminadab, chief of the sons of Uzziel',
 # Nehemiah 12:12-21, heads of priestly houses in the days of Joiakim ("of Seraiah, Meraiah")
 ('Nehemiah 12:12', 'Hananiah'): 'Hananiah, head of the priestly house of Jeremiah',
 ('Nehemiah 12:13', 'Meshullam'): 'Meshullam, head of the priestly house of Ezra', ('Nehemiah 12:13', 'Jehohanan'): 'Jehohanan, head of the priestly house of Amariah',
 ('Nehemiah 12:14', 'Jonathan'): 'Jonathan, head of the priestly house of Melicu', ('Nehemiah 12:14', 'Joseph'): 'Joseph, head of the priestly house of Shebaniah',
 ('Nehemiah 12:15', 'Adna'): 'Adna, head of the priestly house of Harim', ('Nehemiah 12:16', 'Zechariah'): 'Zechariah, head of the priestly house of Iddo',
 ('Nehemiah 12:16', 'Meshullam'): 'Meshullam, head of the priestly house of Ginnethon', ('Nehemiah 12:17', 'Zichri'): 'Zichri, head of the priestly house of Abijah',
 ('Nehemiah 12:18', 'Shammua'): 'Shammua, head of the priestly house of Bilgah', ('Nehemiah 12:18', 'Jehonathan'): 'Jehonathan, head of the priestly house of Shemaiah',
 ('Nehemiah 12:19', 'Mattenai'): 'Mattenai, head of the priestly house of Joiarib', ('Nehemiah 12:19', 'Uzzi'): 'Uzzi, head of the priestly house of Jedaiah',
 ('Nehemiah 12:20', 'Eber'): 'Eber, head of the priestly house of Amok', ('Nehemiah 12:21', 'Hashabiah'): 'Hashabiah, head of the priestly house of Hilkiah',
 ('Nehemiah 12:21', 'Nethaneel'): 'Nethaneel, head of the priestly house of Jedaiah',
 # Ezra 8:16, the "men of understanding" among those sent for
 ('Ezra 8:16', 'Joiarib'): 'Joiarib, man of understanding sent by Ezra',
}

# Clan named for each verse of the clan-ordered lists (used when two people would share a name).
CLANS = {
 'Ezra 10:18': 'Jeshua', 'Ezra 10:20': 'Immer', 'Ezra 10:21': 'Harim', 'Ezra 10:22': 'Pashur', 'Ezra 10:25': 'Parosh',
 'Ezra 10:26': 'Elam', 'Ezra 10:27': 'Zattu', 'Ezra 10:28': 'Bebai', 'Ezra 10:29': 'Bani', 'Ezra 10:30': 'Pahath-moab',
 'Ezra 10:31': 'Harim', 'Ezra 10:32': 'Harim', 'Ezra 10:33': 'Hashum', 'Ezra 10:34': 'Bani', 'Ezra 10:35': 'Bani',
 'Ezra 10:36': 'Bani', 'Ezra 10:37': 'Bani', 'Ezra 10:38': 'Bani', 'Ezra 10:39': 'Bani', 'Ezra 10:40': 'Bani',
 'Ezra 10:41': 'Bani', 'Ezra 10:42': 'Bani', 'Ezra 10:43': 'Nebo',
 'Ezra 8:2': 'Phinehas', 'Ezra 8:3': 'Pharosh', 'Ezra 8:5': 'Shechaniah', 'Ezra 8:9': 'Joab', 'Ezra 8:10': 'Shelomith',
 'Ezra 8:13': 'Adonikam', 'Ezra 8:14': 'Bigvai', 'Ezra 8:19': 'Merari',
 '2 Chronicles 29:12': 'Kohath', '2 Chronicles 29:13': 'Asaph', '2 Chronicles 29:14': 'Heman',
}
