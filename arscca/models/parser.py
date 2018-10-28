from datetime import date as Date
import requests
from bs4 import BeautifulSoup
from .driver import Driver
import pdb
import re
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
            }

    DATE_REGEX = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')

    def __init__(self, url):
        self.url = url

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
            driver = Driver()

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

        self.drivers.sort(key=Driver.fastest_pax_time)
        for index, driver in enumerate(self.drivers):
            driver.position_pax = index + 1

        self.drivers.sort(key=Driver.fastest_time)
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









if __name__ == '__main__':

    url = 'http://arscca.org/index.php?option=com_content&view=article&id=398:2018-solo-ii-event-6-final&catid=125&Itemid=103'

    parser = Parser(url)
    parser.parse()
    parser.rank_drivers()
    pdb.set_trace()
