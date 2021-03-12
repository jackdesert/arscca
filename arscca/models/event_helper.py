"""
These helpers are used in the views
"""


class TwoCourseEventHelper:
    """
    For two course drivers
    """

    COMBINED_SCORING = (
        'Score is computed by adding best morning run to the best afternoon run.',
    )

    BEST_TIME_SCORING = "Governor's Cup score is best time of the day."

    CUMULATIVE_SCORING = 'Cumulative score is the cumulative total of all runs'

    PAX_SCORING = 'PAX Score is Score * PAX Factor'

    # This is a string
    PENALTY_SCORING = (
        'Two seconds are added for each pylon. '
        'That is, 29.723+1 is counted as 31.723 seconds.'
    )

    # This is a string
    PERCENTILE_SCORING = (
        'Position (Percentile) is the percentage of scoring '
        'drivers who were faster than you. See '
        '<a href="https://en.wikipedia.org/wiki/Percentile_rank">Percentile Rank.</a>'
    )

    PRIMARY_SCORE_LABEL = 'Score*'
    SECONDARY_SCORE_LABEL = 'PAX SCORE*'

    PRIMARY_RANK_LABEL = 'Position (Overall)'
    SECONDARY_RANK_LABEL = 'Position (PAX)'

    # run segregation means a (red) line will be place between am and pm runs
    SEGREGATE_RUNS = True

    DYNAMIC_BIN_WIDTH = False

    @classmethod
    def segregate_runs(cls):
        # Tells whether page should show a (red) line between am and pm runs
        return True

    @classmethod
    def has_pax(cls):
        """
        Autocross events have PAX. Rallycross does not.
        """
        return True

    @classmethod
    def scoring(cls):
        return [
            cls.COMBINED_SCORING,
            cls.PENALTY_SCORING,
            cls.PAX_SCORING,
            cls.PERCENTILE_SCORING,
        ]

    @classmethod
    def dynamic_bin_width(cls):
        """
        The bin width to use in the histogram
        """
        return cls.DYNAMIC_BIN_WIDTH

    @classmethod
    def properties(cls):
        """
        All the things needed to flesh out the html
        """
        return dict(
            scoring=cls.scoring(),
            has_pax=cls.has_pax(),
            primary_score_label=cls.PRIMARY_SCORE_LABEL,
            secondary_score_label=cls.SECONDARY_SCORE_LABEL,
            segregate_runs=cls.SEGREGATE_RUNS,
            primary_rank_label=cls.PRIMARY_RANK_LABEL,
            secondary_rank_label=cls.SECONDARY_RANK_LABEL,
        )


class OneCourseEventHelper(TwoCourseEventHelper):
    """
    For one course drivers
    """

    SEGREGATE_RUNS = False
    DYNAMIC_BIN_WIDTH = False

    @classmethod
    def scoring(cls):
        return [
            cls.BEST_TIME_SCORING,
            cls.PENALTY_SCORING,
            cls.PAX_SCORING,
            cls.PERCENTILE_SCORING,
        ]

    @classmethod
    def segregate_runs(cls):
        return False


class RallyEventHelper(TwoCourseEventHelper):
    """
    For rally drivers
    """

    PRIMARY_SCORE_LABEL = 'Cumulative Score'
    SECONDARY_SCORE_LABEL = 'Best Run*'
    SEGREGATE_RUNS = False

    SECONDARY_RANK_LABEL = 'Position (Best&nbsp;Run)'
    DYNAMIC_BIN_WIDTH = True

    @classmethod
    def has_pax(cls):
        """
        Autocross events have PAX. Rallycross does not.
        """
        return False

    @classmethod
    def scoring(cls):
        return [cls.CUMULATIVE_SCORING, cls.PENALTY_SCORING, cls.PERCENTILE_SCORING]

    @classmethod
    def segregate_runs(cls):
        return False


if __name__ == '__main__':
    helper = RallyEventHelper
    props = helper.properties()
    import pdb
    pdb.set_trace()
    1
