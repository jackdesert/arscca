import pdb

class StandardEventHelper:


    COMBINED_SCORING = 'Score is computed by adding best morning run to the best afternoon run.',

    BEST_TIME_SCORING = "Governor's Cup score is best time of the day."

    CUMULATIVE_SCORING = 'Score is the cumulative total of all runs'

    PAX_SCORING = 'PAX Score is Score * PAX Factor'

    PENALTY_SCORING = 'Two seconds are added for each pylon. That is, 29.723+1 is counted as 31.723 seconds.'

    PERCENTILE_SCORING = 'Position (Percentile) is the percentage of scoring drivers who were faster than you. See <a href="https://en.wikipedia.org/wiki/Percentile_rank">Percentile Rank.</a>'



    PRIMARY_SCORE_LABEL = 'Score*'
    SECONDARY_SCORE_LABEL = 'PAX SCORE*'


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
    def properties(cls):
        return dict(scoring=cls.scoring(),
                    has_pax=cls.has_pax(),
                    primary_score_label=cls.PRIMARY_SCORE_LABEL,
                    secondary_score_label=cls.SECONDARY_SCORE_LABEL)

class BestTimeEventHelper(StandardEventHelper):


    @classmethod
    def scoring(cls):
        return [cls.BEST_TIME_SCORING,
                cls.PENALTY_SCORING,
                cls.PAX_SCORING,
                cls.PERCENTILE_SCORING]

class RallyEventHelper(StandardEventHelper):

    PRIMARY_SCORE_LABEL = 'Cumulative Score'
    SECONDARY_SCORE_LABEL = 'Best Run*'

    @classmethod
    def has_pax(cls):
        return False

    @classmethod
    def scoring(cls):
        return [cls.CUMULATIVE_SCORING,
               cls.PENALTY_SCORING,
               cls.PERCENTILE_SCORING]



if __name__ == '__main__':
    helper = RallyEventHelper
    props = helper.properties()
    pdb.set_trace()
    1

