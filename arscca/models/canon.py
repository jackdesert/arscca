# This class takes a string as an argument
# and has method to return either the slug or the name

import pdb
import re

class Canon:
    UNDERSCORE = '_'
    SPACE = ' '
    NON_WORD_CHARS = re.compile(r'[^\w]+')
    WHITESPACE_CHARS = re.compile(r'\s+')

    # { website_slug : photo_slug }
    # AKA
    # { erroneous_slug : correct_slug }
    # AKA
    # { associated_slug : canonical_slug }
    ALIASES = {'joshua_mapili': 'josh_mapili',
               'nicholas_mellenthin': 'nick_mellenthin',
               'richard_davis': 'rick_davis',
               'kenneth_hiegel': 'kenny_hiegel',
               'james_express_lane': 'james_lane',
               'philip_rucker': 'phil_rucker',
               'alexander_ross': 'alex_ross',
               'jeff_gibson': 'jeff_gilson',
               'robert_darin_laughard': 'darin_laughard',
               'william_eldridge': 'william_eldredge',
               'robin_steffon': 'steffon_robin',
               'jeffrey_pierce': 'jeff_pierce',
               'charles_cartwright': 'jeff_cartwright',
               'kimberly_hodges': 'kim_fares'}


    def __init__(self, name_or_slug):
        # Old Rallycross scores have name formatted as Last, First
        # So we remove the comma and reverse the names
        if ',' in name_or_slug:
            name_as_list = name_or_slug.split(',')
            name_as_list.reverse()
            name_or_slug = ' '.join(name_as_list)

        self._canonical_slug = self._build_canonical_slug(name_or_slug)

    @property
    def slug(self):
        return self._canonical_slug

    @property
    def name(self):
        return self.slug.replace(self.UNDERSCORE, self.SPACE).title()

    def _build_canonical_slug(self, name_or_slug):
        output = name_or_slug.strip()
        output = self.WHITESPACE_CHARS.sub(self.UNDERSCORE, output)
        output = self.NON_WORD_CHARS.sub('', output)
        output = output.lower()
        output = self.ALIASES.get(output) or output
        return output
