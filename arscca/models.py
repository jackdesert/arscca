

from decimal import Decimal
class Pax:
    # Pax data from
    # http://www.azsolo.com/backup/index.php/car-classes-and-rules/pax-scoring-system
    # (Hyphens removed)
    FACTORS = dict( AM   = 1.000,
                    AS   = 0.814,
                    ASP  = 0.848,
                    BM   = 0.956,
                    BP   = 0.860,
                    BS   = 0.808,
                    BSP  = 0.846,
                    CAMC = 0.816,
                    CAMS = 0.831,
                    CAMT = 0.807,
                    CM   = 0.890,
                    CP   = 0.847,
                    CS   = 0.805,
                    CSP  = 0.857,
                    DM   = 0.895,
                    DP   = 0.858,
                    DS   = 0.794,
                    DSP  = 0.835,
                    EM   = 0.894,
                    EP   = 0.850,
                    ES   = 0.787,
                    ESP  = 0.828,
                    FM   = 0.904,
                    FP   = 0.863,
                    FS   = 0.797,
                    FSAE = 0.958,
                    FSP  = 0.819,
                    GS   = 0.786,
                    HCR  = 0.812,
                    HCS  = 0.791,
                    HS   = 0.781,
                    JA   = 0.855,
                    JB   = 0.825,
                    JC   = 0.718,
                    KM   = 0.928,
                    SM   = 0.853,
                    SMF  = 0.839,
                    SS   = 0.817,
                    SSC  = 0.806,
                    SSM  = 0.871,
                    SSP  = 0.852,
                    SSR  = 0.838,
                    STH  = 0.811,
                    STP  = 0.815,
                    STR  = 0.823,
                    STS  = 0.810,
                    STU  = 0.824,
                    STX  = 0.813,
                    XP   = 0.884,)



    @classmethod
    def factor(cls, car_class):
        car_class = car_class.upper()
        # Remove Ladies designation
        if car_class.endswith('L'):
            car_class = car_class[0:-1]
        factor = cls.FACTORS[car_class]
        return Decimal(factor)



import re
from decimal import Decimal

class Driver:
    DNF_REGEX     = re.compile('dnf', re.IGNORECASE)
    PENALTY_REGEX = re.compile('\+')

    def __init__(self):
        pass

    def pax_factor(self):
        return Pax.factor(self.car_class)


    def fastest_time(self):
        runs = [self.run_1,
                self.run_2,
                self.run_3,
                self.run_4,
                self.run_5,
                self.run_6]

        times = [self.time_from_string(r) for r in runs]
        return min(times)

    def fastest_pax_time(self):
        fastest = self.fastest_time() * self.pax_factor()
        if fastest == Decimal('inf'):
            return fastest
        else:
            return fastest.quantize(Decimal('.001'))

    def time_from_string(self, string):
        if self.DNF_REGEX.search(string) or (string == '\xa0'):
            return Decimal('inf')
        if self.PENALTY_REGEX.search(string):
            time, delay = string.split('+')
            time = Decimal(time)
            delay = int(delay)
        else:
            time = Decimal(string)
            delay = 0

        return time + delay

    def print(self):
        print('')
        print(f'name          {self.name}')
        print(f'car_number    {self.car_number}')
        print(f'car_class     {self.car_class}')
        print(f'car_model     {self.car_model}')
        print(f'run_1         {self.run_1}')
        print(f'run_2         {self.run_2}')
        print(f'run_3         {self.run_3}')
        print(f'run_4         {self.run_4}')
        print(f'run_5         {self.run_5}')
        print(f'run_6         {self.run_6}')
        print(f'fastest_time  {self.fastest_time()}')
        print(f'fastest_pax   {self.fastest_pax_time()}')


import requests
from bs4 import BeautifulSoup
import pdb
class Parser:

    def __init__(self, url):
        self.url = url

    def parse(self):
        rr = requests.get(url, allow_redirects=False, timeout=10)
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
        return drivers








if __name__ == '__main__':
    url = 'http://arscca.org/index.php?option=com_content&view=article&id=398:2018-solo-ii-event-6-final&catid=125&Itemid=103'

    parser = Parser(url)
    drivers = parser.parse()
    for driver in drivers:
        driver.print()
