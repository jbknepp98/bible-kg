"""Conservative chronology: maps Theographic's Ussher-based years onto the dates conservative evangelical scholarship
uses (Reformation Study Bible chronology), so events, verse years and people share one timeline with the curated
king and book dates.

Anchors are events whose conservative date is well established; every other year is placed by linear
interpolation between the two anchors around it, which keeps the source's order and spacing within each era.
  - Patriarchs: 430-year sojourn in Egypt (Exodus 12:40), Abraham born c. 2166 BC
  - Exodus 1446 BC (1 Kings 6:1), conquest 1406 BC
  - Saul c. 1050, David 1010, Solomon 970, temple begun 966, kingdom divided 931 BC
  - Divided kingdom: Thiele's reign dates (accession or co-regency year)
  - Exile and after, and the New Testament: the source's dates are kept
Before Abraham the source's genealogical intervals are kept and shifted with Abraham; conservative scholarship does
not fix dates for this period, which the dating label says.
All years are signed integers, negative = BC (the project convention).
"""

# (event title in Theographic, source start year, conservative start year)
ANCHORS = [
 ('Birth of Abraham', -1995, -2166),
 ('Birth of Isaac', -1895, -2066),
 ('Birth of Jacob and Esau', -1835, -2006),
 ('Birth of Joseph', -1744, -1916),
 ('Joseph sold to Egypt', -1727, -1899),
 ('Joseph Promoted in Egypt', -1714, -1886),
 ("Joseph's brothers return to Egypt", -1705, -1876),   # Jacob's family moves to Egypt
 ('Death of Joseph', -1634, -1806),
 ('Birth of Moses', -1570, -1526),
 ('Exodus from Egypt', -1490, -1446),
 ('Death of Moses', -1451, -1406),
 ('Reign of Saul', -1094, -1050),
 ('Reign of David', -1054, -1010),
 ('Reign of Solomon', -1014, -970),
 ("Construction of Solomon's Temple", -1011, -966),
 ('Reign of Rehoboam', -974, -931),
 ('Reign of Ahab', -917, -874),
 ('Reign of Jehu', -885, -841),
 ('Reign of Jehoahaz', -856, -814),                     # son of Jehu
 ('Reign of Jehoash', -839, -798),
 ('Reign of Amaziah', -838, -796),
 ('Reign of Jeroboam II', -824, -793),
 ('Reign of Uzziah', -809, -792),
 ('Reign of Zachariah', -783, -753),                   # Thiele has no interregnum after Jeroboam II
 ('Reign of Shallum', -771, -752),                     # Shallum's month and Menahem's accession
 ('Death of Uzziah', -757, -740),                       # Isaiah 6:1
 ('Reign of Ahaz', -741, -735),
 ('Reign of Hoshea', -729, -732),
 ('Reign of Hezekiah', -725, -715),
 ('Reign of Manasseh', -696, -686),                    # sole reign from Hezekiah's death (Thiele)
 ('Reign of Josiah', -639, -640),
 ('Reign of Jehoiakim', -608, -609),
 ('Prophecies of Daniel', -605, -605),                  # first deportation, Daniel 1:1
 ('Reign of Zedekiah', -596, -597),
 ('Prophecies of Haggai', -519, -520),
 (None, -400, -400),                                   # source dates kept from here on
]
_PTS = [(s, t) for _, s, t in ANCHORS]
assert all(a[0] < b[0] and a[1] < b[1] for a, b in zip(_PTS, _PTS[1:])), 'anchors must increase in both columns'

BASIS = 'Conservative chronology (Reformation Study Bible: early Exodus 1446 BC, Thiele kings), mapped from Theographic'
BASIS_KEPT = 'Theographic (conventional historical dates; unchanged)'
BASIS_PRIMEVAL = 'Genealogies of Genesis counted back from Abraham (c. 2166 BC); conservative scholarship fixes no date'

def map_year(y):
    """Map a source (Ussher-based) year, possibly fractional, to the conservative timeline."""
    if y is None: return None
    if y <= _PTS[0][0]:
        return y + (_PTS[0][1] - _PTS[0][0])              # primeval: shift with Abraham
    if y >= _PTS[-1][0]:
        return y
    for (s0, t0), (s1, t1) in zip(_PTS, _PTS[1:]):
        if s0 <= y <= s1:
            return t0 + (y - s0) * (t1 - t0) / (s1 - s0)

def map_int(y):
    return None if y is None else int(round(map_year(y)))

def basis(y):
    if y is not None and y < _PTS[0][0]: return BASIS_PRIMEVAL
    if y is not None and y >= _PTS[-1][0]: return BASIS_KEPT
    return BASIS

def basis_short(y):
    # for columns limited to 40 characters (verse.dating_basis)
    if y is not None and y < _PTS[0][0]: return 'Genesis genealogies (no fixed date)'
    if y is not None and y >= _PTS[-1][0]: return 'Theographic (unchanged)'
    return 'Conservative chronology'

def label(y):
    return None if y is None else (f'{-y} BC' if y < 0 else f'AD {y}')
