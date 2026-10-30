# Curated corrections to Theographic event titles, following the project naming rules (no parentheses,
# no scripture references). Keyed by "by_title:<source title>".
RENAMES = {
 # 'Southern Kingdom (Judah)' / 'Northern Kingdom (Israel)'
 'by_title:Southern Kingdom (Judah)': 'Southern Kingdom of Judah',
 'by_title:Northern Kingdom (Israel)': 'Northern Kingdom of Israel',
 # 2 Chronicles 21:17 calls Ahaziah Jehoahaz; 1 Chronicles 3:15 / Jeremiah 22:11 call Jehoahaz Shallum
 'by_title:Reign of Ahaziah (Jehoahaz)': 'Reign of Ahaziah, also called Jehoahaz',
 'by_title:Reign of Johoahaz (Shallum)': 'Reign of Jehoahaz, also called Shallum',   # also fixes the source's "Johoahaz"
}
# Dates: see chronology.py (conservative timeline mapped from Theographic's Ussher-based years).

# Duration corrections where the source contradicts scripture.
DURATION_FIXES = {
 'Lifetime of Jacob': '147Y',   # Genesis 47:28 "the whole age of Jacob was an hundred forty and seven years" (source: 180Y, Isaac's age)
}
