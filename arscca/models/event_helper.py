import pdb

class TwoCourseEventHelper:


    COMBINED_SCORING = 'Score is computed by adding best morning run to the best afternoon run.',

    BEST_TIME_SCORING = "Governor's Cup score is best time of the day."

    CUMULATIVE_SCORING = 'Cumulative score is the cumulative total of all runs'

    PAX_SCORING = 'PAX Score is Score * PAX Factor'

    PENALTY_SCORING = 'Two seconds are added for each pylon. That is, 29.723+1 is counted as 31.723 seconds.'

    PERCENTILE_SCORING = 'Position (Percentile) is the percentage of scoring drivers who were faster than you. See <a href="https://en.wikipedia.org/wiki/Percentile_rank">Percentile Rank.</a>'



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
        return True

    @classmethod
    def scoring(cls):
        return [cls.COMBINED_SCORING,
               cls.PENALTY_SCORING,
               cls.PAX_SCORING,
               cls.PERCENTILE_SCORING]

    @classmethod
    def dynamic_bin_width(cls):
        return cls.DYNAMIC_BIN_WIDTH

    @classmethod
    def properties(cls):
        return dict(scoring=cls.scoring(),
                    has_pax=cls.has_pax(),
                    primary_score_label=cls.PRIMARY_SCORE_LABEL,
                    secondary_score_label=cls.SECONDARY_SCORE_LABEL,
                    segregate_runs=cls.SEGREGATE_RUNS,
                    primary_rank_label=cls.PRIMARY_RANK_LABEL,
                    secondary_rank_label=cls.SECONDARY_RANK_LABEL)

class OneCourseEventHelper(TwoCourseEventHelper):

    SEGREGATE_RUNS = False
    DYNAMIC_BIN_WIDTH = False

    @classmethod
    def scoring(cls):
        return [cls.BEST_TIME_SCORING,
                cls.PENALTY_SCORING,
                cls.PAX_SCORING,
                cls.PERCENTILE_SCORING]

    @classmethod
    def segregate_runs(cls):
        return False

class RallyEventHelper(TwoCourseEventHelper):

    PRIMARY_SCORE_LABEL = 'Cumulative Score'
    SECONDARY_SCORE_LABEL = 'Best Run*'
    SEGREGATE_RUNS = False

    SECONDARY_RANK_LABEL = 'Position (Best&nbsp;Run)'
    DYNAMIC_BIN_WIDTH = True

    @classmethod
    def has_pax(cls):
        return False

    @classmethod
    def scoring(cls):
        return [cls.CUMULATIVE_SCORING,
               cls.PENALTY_SCORING,
               cls.PERCENTILE_SCORING]

    @classmethod
    def segregate_runs(cls):
        return False


if __name__ == '__main__':
    helper = RallyEventHelper
    props = helper.properties()
    pdb.set_trace()
    1

