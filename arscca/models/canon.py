"""
This class takes a string as an argument
and has method to return either the slug or the name
"""

import re
from types import MappingProxyType


class Canon:
    """
    Used to generate the canonical version of a driver's name.
    And also to generate a driver slug.
    """

    UNDERSCORE = '_'
    SPACE = ' '
    NON_WORD_CHARS = re.compile(r'[^\w]+')
    WHITESPACE_CHARS = re.compile(r'\s+')

    # ALIASES exists mostly because of mispellings in legacy results.
    # But also because sometimes a driver registers under
    # their full name, and other times under their shortened, or nick name.
    #
    # Make sure the VALUE references the photo filename
    #
    # { website_slug : photo_slug }
    # AKA
    # { erroneous_slug : correct_slug }
    # AKA
    # { associated_slug : canonical_slug }
    ALIASES = MappingProxyType(
        {
            # NICKNAMES
            'alexander_hood': 'alex_hood',
            'alexander_ross': 'alex_ross',
            'charles_cartwright': 'jeff_cartwright',
            'james_express_lane': 'james_lane',  # TWO
            'james_fast_lane': 'james_lane',  # TWO
            'jeff_gibson': 'jeff_gilson',
            'jeffrey_pierce': 'jeff_pierce',
            'joshua_mapili': 'josh_mapili',
            'joshua_spear': 'josh_spear',
            'kenneth_hiegel': 'kenny_hiegel',  # ONE NICK, TWO MISP
            'kimberly_hodges': 'kim_fares',
            'nicholas_mellenthin': 'nick_mellenthin',
            'philip_rucker': 'phil_rucker',
            'richard_davis': 'rick_davis',
            'robert_darin_laughard': 'darin_laughard',  # TWO NICKS
            'robert_laughard': 'darin_laughard',  # TWO NICKS
            'robin_steffon': 'steffon_robin',
            'william_eldridge': 'william_eldredge',
            'christopher_edens': 'chris_edens',
            'jarf_hobbs': 'jeff_hobbs',
            'kacy_beck_abunasrah': 'kacy_beck',  # ONE NICK, ONE MISP
            'lacie_barkley': 'lacie_edens',
            'sparkles_barkley': 'david_barkley',
            'tal_penfound': 'taliessin_penfound',
            'vincent_parker': 'vince_parker',
            'bokamper_danny': 'bokamper_daniel',
            'bona_rebecca': 'bona_becca',
            'david_lousteau': 'david_lousteau_jr',  # ONE NICK, ONE MISP
            'elsie_richard': 'elsie_rick',
            'freed_christopher': 'freed_chris',
            'stafford_stephen': 'stafford_steve',
            'elizabeth_yarboro': 'liz_yarboro',
            # PRIVACY REQUESTS
            'griff_ferrell': 'glyph_ferrule',
            # MISSPELLINGS FOUND VIA FondMemory
            'asher_wunderhal': 'asher_wunderl',  # Is this the correct spelling?
            'blake_alverado': 'blake_alvarado',
            'brady_coretz': 'brady_loretz',  # TWO
            'bradey_loretz': 'brady_loretz',  # TWO
            'brent_blankinship': 'brent_blankenship',
            'adam_catorette': 'adam_cadorette',
            'adam_nix': 'adam_hix',  # spelling?
            'kazy_beck': 'kacy_beck',  # MULTIPL
            'andrew_lydecky': 'andrew_lydecker',
            'bentley_brissom': 'bentley_grissom',  # TWO
            'bentley_grissom_hatch': 'bentley_grissom',  # TWO
            'brandan_mellenthin': 'brandon_mellenthin',
            'bruce_hulbut': 'bruce_hurlbut',
            'cameron_haskins': 'cameron_hoskins',  # spelling?
            'chad_langly': 'chad_langley',  # spelling?
            'chase_nufen': 'chase_nufer',
            'christopher_weigand': 'christopher_weiand',
            'chris_weigand': 'christopher_weiand',
            'cody_langly': 'cody_langley',  # spelling?
            'corey_pettet': 'corey_pettett',  # THREE
            'corey_pettit': 'corey_pettett',  # THREE
            'cory_pettit': 'corey_pettett',  # THREE
            'curtis_perrott': 'curtis_parrott',
            'dale_gseccman': 'dale_gsellman',  # TWO. spelling?
            'gseccman_d': 'dale_gsellman',  # TWO. spelling?
            'dale_hurle': 'dale_hurley',
            'danah_meade': 'danah_mead',
            'daniel_barshart': 'daniel_barghart',  # spelling?
            'dean_lyon': 'dean_lyons',
            'edward_abihabib': 'edouard_abihabib',
            'ellia_gildner': 'ellis_gildner',  # TWO
            'ellis_gilner': 'ellis_gildner',  # TWO
            'gary_reynold': 'gary_reynolds',
            'gordan_gibson': 'gordon_gibson',  # THREE
            'gorden_gibson': 'gordon_gibson',  # THREE
            'gordon': 'gordon_gibson',  # THREE
            'ian_ferrerll': 'ian_ferrell',
            'isabel_santos': 'izabel_santos',  # TWO
            'isabella_santos': 'izabel_santos',  # TWO
            'james_powel': 'james_powell',
            'john_seaton': 'jon_seaton',  # TWO
            'jon_seatoin': 'jon_seaton',  # TWO
            'jonathan_jacson': 'jonathan_jackson',
            'josh_mapih': 'josh_mapili',  # THREE MISPELLINGS, one nick
            'josh_mepin': 'josh_mapili',  # THREE MISPELLINGS, one nick
            'joshua_mapiu': 'josh_mapili',  # THREE MISPELLINGS, one nick
            'jp_kvetko': 'john_kvetko',
            'kaylie_hall': 'kaylie_hall',
            'kaylee_costello': 'kayleigh_costello',  # TWO
            'kayligh_costello': 'kayleigh_costello',  # TWO
            'kaylee_hall': 'kaylie_hall',
            'kenny_hiegal': 'kenny_hiegel',  # ONE NICK, TWO MISP
            'kenny_kiegel': 'kenny_hiegel',  # ONE NICK, TWO MISP
            'kerry_emert': 'kerry_emmert',
            'kevin_abbot': 'kevin_abbott',
            'kevin_balte': 'kevin_baltz',
            'kyle_gauthia': 'kyle_gauthier',
            'lance_saveille': 'lance_saville',
            'stephen_edmister': 'stephen_edmisten',
            'stephen_gleeson': 'stephen_gleason',
            'steven_elliot': 'steven_elliott',
            'stuart_bennet': 'stuart_bennett',  # TWO
            'stuar_bennett': 'stuart_bennett',  # TWO
            'suart_leiby': 'stuart_leiby',
            'william_eldrrdge': 'william_eldredge',
            'xach_shaddox': 'zach_shaddox',
            'robert_bennet': 'robert_bennett',
            'phliip_clamon': 'philip_clamon',
            'craiglow_berry': 'craiglow_barry',
            'daily_jason': 'dailey_jason',
            'davis_chelly': 'davis_chelle',
            'lousteau_jr_davis': 'david_lousteau_jr',  # ONE NICK, TWO MISP
            'david_louseau': 'david_lousteau_jr',  # ONE NICK, TWO MISP
            'sidney_degrasse': 'sidney_degrass',
            'robert_dorlague': 'robert_dorlaque',
            'carl_dunn': 'karl_dunn',
            'lawren_hardy': 'lauren_hardy',
            'matt_lieblong': 'matthew_lieblong',
            'sharon_lousteau': 'sher_lousteau',
            'phillip_martinez': 'philip_martinez',
            'jennifer_mathers': 'jennifer_mather',
            'jenniffer_mccrory': 'jennifer_mccrory',
            'milan_rakid': 'milan_rakich',  # TWO
            'milan_rakish': 'milan_rakich',  # TWO
            'saugeeth_sammul': 'sangeeth_samuel',
            'matt_setliff': 'matthew_setliff',  # TWO
            'matt_setiff': 'matthew_setliff',  # TWO
            'scott_selfie': 'scott_silfies',
            'jonathan_stanley': 'johnathan_stanley',  # spelling?
            'ryan_stempke': 'ryan_stampke',
            'zaxh_tucker': 'zach_tucker',
            'peyton_edwards': 'payton_edwards',
            'chris_stevens': 'chris_stephens',
            # QUESTIONS?
            # bill_holt / bill_hoak
            # 'gary_nufen': 'gary_newford', # spelling?
        }
    )

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
        """
        The url-friendly version of their name.
        """
        return self._canonical_slug

    @property
    def name(self):
        """
        Returns the driver's canonical name.
        """
        return self.slug.replace(self.UNDERSCORE, self.SPACE).title()

    def _build_canonical_slug(self, name_or_slug):
        output = name_or_slug.strip()
        output = self.WHITESPACE_CHARS.sub(self.UNDERSCORE, output)
        output = self.NON_WORD_CHARS.sub('', output)
        output = output.lower()
        output = self.ALIASES.get(output) or output
        return output
