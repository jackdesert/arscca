from collections import defaultdict
from glob import glob
from threading import Lock
import pdb
import re

class PublishedEvent:
    # URL_BASE + id maps to the location of FINAL results
    # Required params: ['com_content', 'view', 'id']
    URL_BASE = 'http://arscca.org/index.php?option=com_content&view=article&id='
    LOCK = Lock()
    FILENAME_REGEX = re.compile('/(.+)__(.+)\.html')

    # DATES maps event dates (used to build url in pyramid)
    # to joomla ids (where official results are stored)
    __DATES_BY_YEAR = defaultdict(list)


            # 2019
    L = {'2019-03-24' : 444,
        '2019-04-28' : 452,
        '2019-05-19' : 456,
        '2019-06-16' : 460,
        '2019-07-14' : 464,
        '2019-08-11' : 469,
        '2019-09-21' : 477,
        '2019-09-22' : 481,
        '2019-10-13' : 488,
        '2019-10-26' : 492,
        '2019-12-08' : 508,
        '2019-11-09' : 496, # Rallyx
        '2019-04-13' : 446, # Rallyx
        '2019-09-14' : 474, # Rallyx
        '2019-10-05' : 485, # Rallyx

        # 2018
        '2018-03-18' : 372,
        '2018-04-15' : 379,
        '2018-05-26' : 386,
        '2018-06-09' : 393,
        '2018-06-10' : 397,
        '2018-06-24' : 398,
        '2018-07-21' : 409,
        '2018-07-22' : 413,
        '2018-08-11a': 421,
        '2018-08-11b': 416,
        '2018-09-22' : 425,
        '2018-09-23' : 429,
        '2018-10-21' : 435,
        '2018-11-02' : 437, # Rallyx
        '2018-10-05' : 430, # Rallyx
        '2018-06-01' : 389, # Rallyx
        '2018-05-06' : 380, # Rallyx
        '2018-03-24' : 375, # Rallyx



        # 2017
        '2017-12-03': 367,
        '2017-11-12': 360,
        '2017-11-11': 356,
        '2017-10-22': 351,
        '2017-09-24': 348, # Gov cup
        '2017-09-23': 344,
        '2017-08-20': 337,
        '2017-08-19': 333,
        '2017-07-16': 329,
        '2017-06-11': 325,
        '2017-05-21': 318,
        '2017-04-02': 310,
        '2017-03-19': 306,
        '2017-11-18': 361, # Rallyx
        '2017-09-16': 338, # Rallyx
        '2017-05-27': 319, # Rallyx
        '2017-04-15': 313, # Rallyx

        # 2016
        '2016-12-04': 299,
        '2016-10-16': 293,
        '2016-10-15': 286,
        '2016-09-25': 285,
        '2016-09-24': 280,
        '2016-07-17': 273,
        '2016-05-22': 267,
        '2016-04-03': 260,
        '2016-04-02': 256,
        '2016-03-20': 255,
        '2016-11-19': 294, # Rallyx
        '2016-07-30': 275, # Rallyx
        '2016-04-09': 265, # Rallyx


        # 2015
        '2015-12-06': 250,
        '2015-10-26': 245,  # RESULTS IN BLUE; Car COLORS only (date was 07-19; changed to 10-26 based on source code of web page.)
        '2015-09-27': 241,
        '2015-08-02': 233, # Single Day Event
        '2015-07-19': 227,
        '2015-07-18': 223,
        '2015-06-28': 220,
        '2015-05-17': 212, # Only has three runs
        '2015-05-16': 208,
        '2015-03-22': 206,
        '2015-08-22': 235, # RallyX
        '2015-06-20': 216, # RallyX


        }

    def __init__(self, date):
        self._date =  date

    @property
    def url(self):
        year = self._date[0:4]
        events = self.dates_by_year().get(year)
        if events:
            for date, joomla_id in events:
                if date == self._date:
                    return f'{self.URL_BASE}{joomla_id}'
        return None

    @classmethod
    def dates_by_year(cls):
        with cls.LOCK:
            if cls.__DATES_BY_YEAR:
                return cls.__DATES_BY_YEAR

            output = defaultdict(list)
            for filename in glob('archive/*.html'):
                search = cls.FILENAME_REGEX.search(filename)
                date = search[1]
                joomla_id = int(search[2])
                year = date[0:4]
                output[year].append((date, joomla_id))

            for year, events in sorted(output.items(), reverse=True):
                cls.__DATES_BY_YEAR[year] = sorted(events, reverse=True)

            return cls.__DATES_BY_YEAR

if __name__ == '__main__':
    import requests
    HOST = 'http://localhost:6543'
    # HOST = 'http://arscca.jackdesert.com'
    dates = PublishedEvent.dates_by_year()


    for date, joomla_id in PublishedEvent.DATES_BY_YEAR.items():
        url = f'{HOST}/events/{date}?cb=1'
        print(f'Parsing {date}')

        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            print(f'ERROR: {url}')
