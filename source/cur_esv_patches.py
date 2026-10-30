# Corrections applied to the trial ESV import (source: unofficial SQLite dump, BIBLE-Study/SQLite-Databases,
# 2011 text; see gen_esv_trial.py). Verse ids use the project's KJV numbering.
# The ESV text itself is NOT kept in this repository (licensed text); only these small patches and notes are.

EDITION = 'ESV 2011 text (pre-2016 edition), unofficial digital copy, patched'
ATTRIBUTION = ('Scripture quotations are from the ESV® Bible (The Holy Bible, English Standard Version®), '
               '© 2001 by Crossway, a publishing ministry of Good News Publishers. Used by permission. All rights reserved.')

# The 16 verses the ESV leaves out of its main text and places in footnotes. The dump has "See Footnote" for 15
# of them and the footnote wording for Matthew 17:21; all 16 are stored with empty text and this note.
NOT_IN_ESV = ['Matt.17.21', 'Matt.18.11', 'Matt.23.14', 'Mark.7.16', 'Mark.9.44', 'Mark.9.46', 'Mark.11.26',
              'Mark.15.28', 'Luke.17.36', 'Luke.23.17', 'John.5.4', 'Acts.8.37', 'Acts.15.34', 'Acts.24.7',
              'Acts.28.29', 'Rom.16.24']
NOT_IN_ESV_NOTE = ('Not in the ESV main text: Crossway places this verse in a footnote because the earliest '
                   'manuscripts lack it.')

# Text lost or moved where ESV numbering differs from the KJV numbering used here.
PATCHES = {
 '3John.1.14': ('append', ' Peace be to you. The friends greet you. Greet the friends, each by name.',
                'Includes ESV 3 John 15, which the KJV numbering counts as part of verse 14; that text was missing '
                'from the import and was restored.'),
}
NOTES = {
 'Rev.12.17': 'Includes ESV Revelation 12:18 ("And he stood on the sand of the sea"), which the KJV numbering '
              'counts as the start of 13:1.',
}
