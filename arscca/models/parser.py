from .driver import Driver
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
            }

    DATE_REGEX = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')
    REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
    PAX = 'PAX'

    def __init__(self, date, url):
        self.date = date
        self.url = url
        self._point_storage = defaultdict(int)

    def parse(self):
        rr = requests.get(self.url, allow_redirects=False, timeout=10)
        soup = BeautifulSoup(rr.text, 'html.parser')

        # First h2 has title
        self.event_name = soup.find('h2').text.strip().replace('Final', '')

        # First table has datethe event name and date
        date_table = soup('table')[0]
        date_string = date_table('th')[0].text
        self.event_date = self.format_date(date_string)

        # Third table has driver results
        table = soup('table')[2]
        data = []
        for tr in table('tr'):
            row = [td.text for td in tr('td')]
            if row:
                data.append(row)

        drivers = []
        # Two rows are used to represent a single driver
        for row_idx in range(0, len(data), 2):
            driver = Driver(self._year())

            driver.id         = row_idx
            driver.car_class  = data[row_idx][1]
            driver.car_number = data[row_idx][2]
            driver.name       = data[row_idx][3].title()
            driver.car_model  = data[row_idx][4]
            driver.run_1      = data[row_idx][7]
            driver.run_2      = data[row_idx][8]
            driver.run_3      = data[row_idx][9]
            driver.run_4      = data[row_idx + 1][7]
            driver.run_5      = data[row_idx + 1][8]
            driver.run_6      = data[row_idx + 1][9]
            drivers.append(driver)
        self.drivers = drivers

    def rank_drivers(self):

        self.drivers.sort(key=Driver.best_combined_pax)
        for index, driver in enumerate(self.drivers):
            driver.position_pax = index + 1

        self._apply_points()

        self.drivers.sort(key=Driver.best_combined)
        for index, driver in enumerate(self.drivers):
            driver.position_overall = index + 1

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

    def _year(self):
        return int(self.date[0:4])

    def _apply_points(self):
        data = defaultdict(dict)
        for index, driver in enumerate(self.drivers):
            if driver.best_combined() == Driver.INF:
                # No points unless you scored
                print(f'{driver.name} did not score')
                continue
            pax_points = self._point(self.PAX)
            if pax_points > 0:
                data[self.PAX][driver.name] = pax_points
            car_class = driver.car_class.lower()
            car_class_points = self._point(car_class)
            if car_class_points > 0:
                data[car_class][driver.name] = car_class_points
            print(f'{driver.name} awarded {pax_points} pax points and {car_class_points} {car_class} points')
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

    url = 'http://arscca.org/index.php?option=com_content&view=article&id=398:2018-solo-ii-event-6-final&catid=125&Itemid=103'

    parser = Parser(url)
    parser.parse()
    parser.rank_drivers()
    pdb.set_trace()
