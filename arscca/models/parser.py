import requests
from bs4 import BeautifulSoup
from .driver import Driver
import pdb
class Parser:

    def __init__(self, url):
        self.url = url

    def parse(self):
        rr = requests.get(self.url, allow_redirects=False, timeout=10)
        soup = BeautifulSoup(rr.text, 'html.parser')
        # grab the third table
        table = soup('table')[2]
        data = []
        for tr in table('tr'):
            row = [td.text for td in tr('td')]
            if row:
                data.append(row)

        drivers = []
        # Two rows are used to represent a single driver
        for row_idx in range(0, len(data), 2):
            print(f'row_idx: {row_idx}')
            driver = Driver()

            driver.car_class  = data[row_idx][1]
            driver.car_number = data[row_idx][2]
            driver.name       = data[row_idx][3]
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








if __name__ == '__main__':

    url = 'http://arscca.org/index.php?option=com_content&view=article&id=398:2018-solo-ii-event-6-final&catid=125&Itemid=103'

    parser = Parser(url)
    parser.parse()
    parser.rank_drivers()
    pdb.set_trace()
