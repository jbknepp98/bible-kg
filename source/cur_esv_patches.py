# Corrections applied to the trial ESV import (source: unofficial SQLite dump, BIBLE-Study/SQLite-Databases;
# the 2001 original-edition text, checked against esv.org on 2026-10-29: about 3% of verses differ from the
# current ESV because of Crossway's 2007/2011/2016 revisions; see gen_esv_trial.py). Verse ids use the project's KJV numbering.
# The ESV text itself is NOT kept in this repository (licensed text); only these small patches and notes are.

EDITION = 'ESV 2001 text (original edition), unofficial digital copy, patched'
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

# Psalm 119: the dump glues the next stanza's Hebrew letter heading onto the last verse of each stanza
# ("...forsake me!Beth"). Stripped from verses 8, 16, ... 168.
PS119_LETTERS = ['Aleph', 'Beth', 'Gimel', 'Daleth', 'He', 'Waw', 'Zayin', 'Heth', 'Teth', 'Yodh', 'Kaph', 'Lamedh',
                 'Mem', 'Nun', 'Samekh', 'Ayin', 'Pe', 'Tsadhe', 'Qoph', 'Resh', 'Sin and Shin', 'Taw']

# Notes the dump merged into verse text: moved to the note column.
MOVE_TO_NOTE = {
 'Mark.16.8': ' [Some of the earliest manuscripts do not include 16:9-20.]',
 'John.7.52': ' [The earliest manuscripts do not include John 7:53-8:11]',
}
# Lines the dump wrapped in single brackets that belong to the ESV text (footnoted there): brackets removed.
UNBRACKET = {'Ps.145.13': 'The second line is supplied by one Hebrew manuscript, the Septuagint and the Syriac (ESV footnote).'}

# Where a paragraph or line break was flattened, the dump lost the space ("...made.He said"); a space is restored.
# Inside quotations the closing and opening quotation marks were lost too. These seven were checked against
# esv.org and get '" "' (e.g. John 1:21 "I am not." "Are you the Prophet?"); Jeremiah 51:11 needs only a space.
QUOTE_JOINS = ['Jer.3.22', 'Jer.8.19', 'Mal.1.2', 'John.1.21', 'Acts.25.22', 'Rom.3.13', 'Rev.14.13']
