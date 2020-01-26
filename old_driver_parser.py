arrrrrgh!
We do not use this file anymore

from arscca.models.canon import Canon
from arscca.models.driver import TwoCourseDriver
from arscca.models.driver import OneCourseDriver
from arscca.models.driver import RallyDriver
from arscca.models.event_helper import StandardEventHelper
from arscca.models.event_helper import BestTimeEventHelper
from arscca.models.event_helper import RallyEventHelper
from arscca.models.fond_memory import FondMemory
from arscca.models.util import Util
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import pdb
import re
import redis


class DriverParser:
    BEST_TIME_PARSER_DATES = { '2019-10-26', # Governor's Cup 2019
                               '2018-09-23', # Governor's Cup 2018
                               '2017-09-24', # Governor's Cup 2017
                             }

    RALLY_PARSER_DATES = {
                          # 2019
                          '2019-11-09',
                          '2019-04-13',
                          '2019-09-14',
                          '2019-10-05',

                          # 2018

                          '2018-11-02',
                          '2018-10-05',
                          '2018-06-01',
                          '2018-05-06',
                          '2018-03-24',

                          # 2017
                          '2017-11-18',
                          '2017-09-16',
                          '2017-05-27',
                          '2017-04-15',

                          # 2016
                          '2016-11-19',
                          '2016-07-30',
                          '2016-04-09',

                          # 2015
                          '2015-08-22',
                          '2015-06-20',


                         }


    @classmethod
    def instantiate_correct_type(cls, date, url, live):
        parser = StandardParser(date, url, live)
        if date in cls.BEST_TIME_PARSER_DATES:
            parser = BestTimeParser(date, url, live)
        elif date in cls.RALLY_PARSER_DATES:
            parser = RallyParser(date, url, live)
        return parser


# Instantiate only subclasses of DriverParser
class DriverParser:

    # Standard event has an am course and a pm course
    # Score is best am plus best pm run
    NUM_COURSES = 2
    ROWS_PER_DRIVER = 2

    RESULTS_TABLE_INDEX_DEFAULT = 2
    DRIVER_INSTANTIATOR = TwoCourseDriver
    EVENT_HELPER = StandardEventHelper

    PAX = 'PAX'

    # Most events have 3 runs_upper (morning course)
    # and 3 runs_lower (afternoon_course)
    DEFAULT_RUNS_PER_COURSE = 3
    RUNS_PER_COURSE = defaultdict(lambda: StandardParser.DEFAULT_RUNS_PER_COURSE)
    RUNS_PER_COURSE['2018-06-10'] = 4
    RUNS_PER_COURSE['2019-07-14'] = 4

    NON_POINTS_EVENT_DATES = ['2019-12-08']



    def __init__(self, row_1, row_2):
        self.date = date
        self.url = url
        self.live = live # Boolean
        self._point_storage = defaultdict(int)
        self.runs_per_course = self.RUNS_PER_COURSE[date]
        # self.drivers will be an array
        # self.table_width with be an integer
        # self.event_name will be a string
        # self.data will be a list

    def parse(self):
        self._compile_data()
        self._instantiate_drivers()



    @property
    def table_width(self):
        return len(self._data[0])

    def _rows_per_driver(self):
        if NOT_JUST_WHITESPACE_REGEX.match(self._data[1][0]):
            return 1
        else:
            return 2

    def _instantiate_drivers(self):
        while index < len(self._data):
            rows_for_one_driver = self._data[index : index + self._rows_per_driver]
            driver = self._parse_driver(rows_for_one_driver)
            self.drivers.append(driver)




    @property
    def _run_columns(self):
        return range(self._first_run_column,
                     self._first_run_column + self.runs_per_course)
    def _runs_lower(self, row_idx, data):
        # Note each parser has a different implementation of this method
        try:
            return [data[row_idx + 1][col_idx] for col_idx in self._run_columns]
        except Exception as eee:
            pdb.set_trace()
            1

    def _year(self):
        return int(self.date[0:4])


    @property
    def _results_table_index(self):
        default = self.RESULTS_TABLE_INDEX_DEFAULT

        if self.date < '2017-01-01':
            # Prior to 2017, there is one less column
            return default - 1
        else:
            return default






class TwoCourseDriverParser(DriverParser):
    pass

class OneCourseDriverParser(DriverParser):

    # BestTime (of the day) Event has the same course am and pm
    # Score is best time of the entire day (not counting fun runs)
    NUM_COURSES = 1
    DEFAULT_RUNS_PER_COURSE = 6
    RUNS_PER_COURSE = defaultdict(lambda: BestTimeParser.DEFAULT_RUNS_PER_COURSE)
    DRIVER_INSTANTIATOR = OneCourseDriver
    EVENT_HELPER = BestTimeEventHelper

    @property
    def _run_columns(self):
        return range(self._first_run_column,
                     self._first_run_column + self.runs_per_course)


    def _runs_lower(self, row_idx, data):
        return []

    def _useful_row(self, row):
        # So far BestTimeParser does not add blank rows, so all are useful
        return True


class RallyDriverParser(DriverParser):

    # BestTime (of the day) Event has the same course am and pm
    # Score is best time of the entire day (not counting fun runs)
    NUM_COURSES = 2 # (only one course, but represented by two rows, so set to 2)
    DEFAULT_RUNS_PER_COURSE = 10 # (only one course, but represented by two rows)
    LAST_RUN_COLUMN = 14 # Rally events usually have 10x2 grid
    RUNS_PER_COURSE = defaultdict(lambda: BestTimeParser.DEFAULT_RUNS_PER_COURSE)
    RESULTS_TABLE_INDEX_DEFAULT = 1 # Second table has results
    DRIVER_INSTANTIATOR = RallyDriver
    EVENT_HELPER = RallyEventHelper

    @property
    def _run_columns(self):
        return range(self._first_run_column, self.table_width - 1)

    def _useful_row(self, row):
        # So far RallyParser does not add blank rows, so all are useful
        return True

    def _apply_points(self):
        # No point system for rallycross YET!
        pass


    def _runs_lower(self, row_idx, data):
        runs = super()._runs_lower(row_idx, data)
        runs_to_use = [run for run in runs if self.NOT_JUST_WHITESPACE_REGEX.match(run)]
        return runs_to_use



if __name__ == '__main__':

    date = '2019-07-14'
    url = 'http://arscca.org/index.php?option=com_content&view=article&id=464'

    parser = StandardParser(date, url)
    parser.parse()

    parser.rank_drivers()
    pdb.set_trace()
    1
