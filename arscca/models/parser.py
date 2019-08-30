from arscca.models.driver import Driver
from arscca.models.canon import Canon
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import date as Date
import json
import pdb
import re
import redis
import requests

class Parser:

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
            }

    DATE_REGEX = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')
    D1_OR_D2_REGEX = re.compile('D1|D2')
    REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
    PAX = 'PAX'
    FIRST_RUN_COLUMN = 7

    # Most events have 3 am_runs (morning course)
    # and 3 pm_runs (afternoon_course)
    DEFAULT_RUNS_PER_COURSE = 3
    RUNS_PER_COURSE = defaultdict(lambda: Parser.DEFAULT_RUNS_PER_COURSE)
    RUNS_PER_COURSE['2018-06-10'] = 4
    RUNS_PER_COURSE['2019-07-14'] = 4

    # This filename ends in jinja2 because it is used as a view template
    LIVE_FILENAME = '/home/arscca/arscca-live.jinja2'

    def __init__(self, date, url, live):
        self.date = date
        self.url = url
        self.live = live # Boolean
        self._point_storage = defaultdict(int)
        self.runs_per_course = self.RUNS_PER_COURSE[date]

    def parse(self):
        try:
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
        except:
            pdb.set_trace()
            1

        # First table has datethe event name and date
        date_table = soup('table')[0]
        date_string = date_table('th')[0].text
        self.event_date = self.format_date(date_string)

        # Third table has driver results
        table = soup('table')[2]
        data = []
        for tr in table('tr'):
            row = [td.text for td in tr('td')]
            # Ensure that the seventh column has 'D1' or 'D2'.
            # Otherwise this is a (mostly) blank row
            if row and self.D1_OR_D2_REGEX.match(row[6]):
                data.append(row)

        second_half_started = False
        drivers = []
        # Two rows are used to represent a single driver
        for row_idx in range(0, len(data), 2):
            driver = Driver(self._year())

            driver.id         = row_idx
            driver.car_class  = data[row_idx][1]
            driver.car_number = data[row_idx][2]
            driver.name       = data[row_idx][3].title()
            driver.car_model  = data[row_idx][4]
            driver.am_runs = [data[row_idx][col_idx]     for col_idx in self._run_columns]
            driver.pm_runs = [data[row_idx + 1][col_idx] for col_idx in self._run_columns]
            if driver.best_pm():
                second_half_started = True
            driver.published_best_combined = data[row_idx][-1]
            drivers.append(driver)

        for driver in drivers:
            driver.second_half_started = second_half_started
        self.drivers = drivers

    def rank_drivers(self):

        scores = [driver.best_combined() for driver in self.drivers]
        num_drivers = len([score for score in scores if score < Driver.INF])

        self.drivers.sort(key=Driver.best_combined_pax)
        for index, driver in enumerate(self.drivers):
            if driver.best_combined() < Driver.INF:
                driver.position_pax = index + 1

        if not self.live:
            self._apply_points()

        self.drivers.sort(key=Driver.best_combined)
        for index, driver in enumerate(self.drivers):
            if driver.best_combined() < Driver.INF:
                driver.position_overall = index + 1
                driver.position_percentile = round(100 * index / num_drivers)

        self.drivers.sort(key=Driver.car_class_sortable)
        rank = 1
        last_car_class = self.drivers[0].car_class
        for driver in self.drivers:
            if driver.car_class != last_car_class:
                rank = 1
            driver.position_class = rank
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
        return range(self.FIRST_RUN_COLUMN,
                     self.FIRST_RUN_COLUMN + self.runs_per_course)
    def _year(self):
        return int(self.date[0:4])

    def _apply_points(self):
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












if __name__ == '__main__':

    date = '2019-07-14'
    url = 'http://arscca.org/index.php?option=com_content&view=article&id=464'

    parser = Parser(date, url)
    parser.parse()

    parser.rank_drivers()
    pdb.set_trace()
    1
