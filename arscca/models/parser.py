from arscca.models.canon import Canon
from arscca.models.driver import Driver
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
from datetime import date as Date
import json
import pdb
import re
import redis
import requests


class TableSplitter:
    pass


class Parser:
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


class StandardParser:

    # Standard event has an am course and a pm course
    # Score is best am plus best pm run
    NUM_COURSES = 2
    ROWS_PER_DRIVER = 2

    RESULTS_TABLE_INDEX_DEFAULT = 2
    DRIVER_INSTANTIATOR = TwoCourseDriver
    EVENT_HELPER = StandardEventHelper

    # Required params: ['com_content', 'view', 'id']
    # The only param that changes: 'id'
    # Which view to click on to get the correct 'id': FINAL
    URLS = {

            '2018-03-18' : 'http://arscca.org/index.php?option=com_content&view=article&id=372',
            '2018-04-15' : 'http://arscca.org/index.php?option=com_content&view=article&id=379',
            '2018-05-26' : 'http://arscca.org/index.php?option=com_content&view=article&id=386',
            '2018-06-09' : 'http://arscca.org/index.php?option=com_content&view=article&id=393',
            '2018-06-10' : 'http://arscca.org/index.php?option=com_content&view=article&id=397',
            '2018-06-24' : 'http://arscca.org/index.php?option=com_content&view=article&id=398',
            '2018-07-21' : 'http://arscca.org/index.php?option=com_content&view=article&id=409',
            # 8
            '2018-07-22' : 'http://arscca.org/index.php?option=com_content&view=article&id=413',
            # 9 8/11?
            '2018-08-11a' : 'http://arscca.org/index.php?option=com_content&view=article&id=421',
            # 10 8/11?
            '2018-08-11b' : 'http://arscca.org/index.php?option=com_content&view=article&id=416',

            # 11
            '2018-09-22' : 'http://arscca.org/index.php?option=com_content&view=article&id=425',

            # 12
            '2018-09-23' : 'http://arscca.org/index.php?option=com_content&view=article&id=429',

            # 13
            '2018-10-21' : 'http://arscca.org/index.php?option=com_content&view=article&id=435',

            # 1
            '2019-03-24' : 'http://arscca.org/index.php?option=com_content&view=article&id=444',
            '2019-04-28' : 'http://arscca.org/index.php?option=com_content&view=article&id=452',
            '2019-05-19' : 'http://arscca.org/index.php?option=com_content&view=article&id=456',
            '2019-06-16' : 'http://arscca.org/index.php?option=com_content&view=article&id=460',
            '2019-07-14' : 'http://arscca.org/index.php?option=com_content&view=article&id=464',
            '2019-08-11' : 'http://arscca.org/index.php?option=com_content&view=article&id=469',
            '2019-09-21' : 'http://arscca.org/index.php?option=com_content&view=article&id=477',
            '2019-09-22' : 'http://arscca.org/index.php?option=com_content&view=article&id=481',
            '2019-10-13' : 'http://arscca.org/index.php?option=com_content&view=article&id=488',
            '2019-10-26' : 'http://arscca.org/index.php?option=com_content&view=article&id=492',
            '2019-11-09' : 'http://arscca.org/index.php?option=com_content&view=article&id=496',
            '2019-12-08' : 'http://arscca.org/index.php?option=com_content&view=article&id=508',
            }

    DATE_REGEX = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')
    NOT_JUST_WHITESPACE_REGEX = re.compile('[^\s]')
    REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
    PAX = 'PAX'
    FIRST_RUN_COLUMN_DEFAULT = 7
    PUBLISHED_PRIMARY_SCORE_COLUMN = -1

    # Most events have 3 runs_upper (morning course)
    # and 3 runs_lower (afternoon_course)
    DEFAULT_RUNS_PER_COURSE = 3
    RUNS_PER_COURSE = defaultdict(lambda: StandardParser.DEFAULT_RUNS_PER_COURSE)
    RUNS_PER_COURSE['2018-06-10'] = 4
    RUNS_PER_COURSE['2019-07-14'] = 4

    NON_POINTS_EVENT_DATES = ['2019-12-08']


    # This filename ends in jinja2 because it is used as a view template
    LIVE_FILENAME = '/home/arscca/arscca-live.jinja2'

    def __init__(self, date, url, live):
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

    def _compile_data(self):
        if self.live:
            with open(self.LIVE_FILENAME, 'r') as ff:
                html = ff.read()
        else:
            rr = requests.get(self.url, allow_redirects=False, timeout=10)
            html = rr.text

        soup = BeautifulSoup(html, 'html.parser')


        if self.live:
            self.event_name = f'Live Results {self.date}'
        else:
            # First h2 has title
            self.event_name = soup.find('h2').text.strip().replace('Final', '')

        # First table has datethe event name and date
        date_table = soup('table')[0] # Failure here means file is empty; check twisted
        date_string = date_table('th')[0].text
        self.event_date = self.format_date(date_string)

        # Third table has driver results
        # Except Rally events, it's second table
        table = soup('table')[self._results_table_index]
        data = []
        for tr in table('tr'):
            if tr('a'):
                # Results from 2016 and earlier have two rows of class links
                # that we want to ignore.
                continue
            # Note this skips header row if header is th
            row = [td.text for td in tr('td')]
            if row and self._useful_row(row):
                data.append(row)
        self._data = data


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


    def _useful_row(self, row):
        if len(row) < 6:
            # Events from 2016 and earlier include a summary at the
            # bottom of the table. The summary is only five cols wide.
            return False

        # A useful row as either Name, car, etc
        # OR it has D1|D2 in row[6]
        for item in row[0:7]:
            if self.NOT_JUST_WHITESPACE_REGEX.match(item):
                return True

        return False

    def _parse_drivers(self, data):

        second_half_started = False
        drivers = []
        # StandardParser uses two rows to represent a single driver
        # BestTimeParser uses one row  to represent a single driver
        for row_idx in range(0, len(data), self.NUM_COURSES):
            driver = self.DRIVER_INSTANTIATOR(self._year())

            driver.car_class  = data[row_idx][1]
            driver.car_number = data[row_idx][2]
            driver.name       = Canon(data[row_idx][3]).name

            # Driver id must remain the same between runs for live results
            # in order for highlighted rows to persist.
            driver_slug = Canon(driver.name).slug
            driver.id         = f'{driver_slug}--{driver.car_class}_{driver.car_number}'
            driver.car_model  = data[row_idx][4]
            driver.runs_upper = [data[row_idx][col_idx] for col_idx in self._run_columns]
            driver.runs_lower = self._runs_lower(row_idx, data)
            if driver.best_pm() and not Util.KART_KLASS_REGEX.match(driver.car_class):
                # Second half is triggered when a non-kart-driver has afternoon score
                second_half_started = True
            driver.published_primary_score = data[row_idx][self.PUBLISHED_PRIMARY_SCORE_COLUMN]
            drivers.append(driver)

        for driver in drivers:
            driver.second_half_started = second_half_started
        return drivers

    def rank_drivers(self):

        scores = [driver.primary_score() for driver in self.drivers]
        num_drivers = len([score for score in scores if score < Driver.INF])

        self.drivers.sort(key=self.DRIVER_INSTANTIATOR.secondary_score)
        for index, driver in enumerate(self.drivers):
            if driver.best_combined() < Driver.INF:
                driver.secondary_rank = index + 1

        if not self.live:
            self._apply_points()

        self.drivers.sort(key=self.DRIVER_INSTANTIATOR.primary_score)
        for index, driver in enumerate(self.drivers):
            if driver.best_combined() < Driver.INF:
                driver.primary_rank = index + 1
                driver.percentile_rank = round(100 * index / num_drivers)

        if not self.live:
            self._create_fond_memories()

        self.drivers.sort(key=Driver.car_class_sortable)
        rank = 1
        last_car_class = self.drivers[0].car_class
        for driver in self.drivers:
            if driver.car_class != last_car_class:
                rank = 1
            driver.class_rank = rank
            rank += 1
            last_car_class = driver.car_class

    def format_date(self, string):
        matches = self.DATE_REGEX.search(string)
        if not matches:
            return string
        month = int(matches[1])
        day   = int(matches[2])
        year  = int(matches[3])
        date  = Date(year, month, day)
        return date.strftime('%B %-d, %Y')

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

    def _create_fond_memories(self):
        FondMemory.store_event_name(self.date, self.event_name)
        for driver in self.drivers:
            memory = FondMemory(driver, self.date)
            memory.write()

    def _apply_points(self):
        if self.date in self.NON_POINTS_EVENT_DATES:
            # Test & Tune, Hangover generally not pointed
            return

        data = defaultdict(dict)
        for index, driver in enumerate(self.drivers):
            canonical_driver_name = Canon(driver.name).name

            if driver.best_combined() == Driver.INF:
                # No points unless you scored
                print(f'{canonical_driver_name} did not score')
                continue
            pax_points = self._point(self.PAX)
            if pax_points > 0:
                data[self.PAX][canonical_driver_name] = pax_points
            car_class = driver.car_class.lower()
            car_class_points = self._point(car_class)
            if car_class_points > 0:
                data[car_class][canonical_driver_name] = car_class_points
            print(f'{canonical_driver_name} awarded {pax_points} pax points and {car_class_points} {car_class} points')
        self.REDIS.set(f'points-from-{self.date}', json.dumps(data))

    def _point(self, pax_or_car_class):
        num_drivers_ahead = self._point_storage[pax_or_car_class]
        if num_drivers_ahead == 0 and (pax_or_car_class != self.PAX):
            points = 11
        else:
            points = 10 - num_drivers_ahead

        # points do not go lower than zero
        points = max([0, points])

        self._point_storage[pax_or_car_class] += 1

        return points

    @property
    def _first_run_column(self):
        default = self.FIRST_RUN_COLUMN_DEFAULT

        if self.date < '2017-01-01':
            # Prior to 2017, there is one less column
            return default - 1
        else:
            return default


    @property
    def _results_table_index(self):
        default = self.RESULTS_TABLE_INDEX_DEFAULT

        if self.date < '2017-01-01':
            # Prior to 2017, there is one less column
            return default - 1
        else:
            return default






class BestTimeParser(StandardParser):

    # BestTime (of the day) Event has the same course am and pm
    # Score is best time of the entire day (not counting fun runs)
    NUM_COURSES = 1
    DEFAULT_RUNS_PER_COURSE = 6
    FIRST_RUN_COLUMN_DEFAULT = 6 # This is different because there is no "D1" or "D2" column
    RUNS_PER_COURSE = defaultdict(lambda: BestTimeParser.DEFAULT_RUNS_PER_COURSE)
    PUBLISHED_PRIMARY_SCORE_COLUMN = -2
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


class RallyParser(StandardParser):

    # BestTime (of the day) Event has the same course am and pm
    # Score is best time of the entire day (not counting fun runs)
    NUM_COURSES = 2 # (only one course, but represented by two rows, so set to 2)
    DEFAULT_RUNS_PER_COURSE = 10 # (only one course, but represented by two rows)
    FIRST_RUN_COLUMN_DEFAULT = 5
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
