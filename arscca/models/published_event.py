from collections import defaultdict
from datetime import datetime
from glob import glob
from threading import Lock
import pdb
import re

from arscca.models.shared import Shared


class PublishedEvent:
    # URL_BASE + id maps to the location of FINAL results
    # Required params: ['com_content', 'view', 'id']
    URL_BASE = 'http://arscca.org/event_results'
    LOCK = Lock()
    FILENAME_REGEX = re.compile(r'/(\d{4})/(.+)__(.+)\.html')

    DIRT_SURFACE = 'dirt'
    TARMAC_SURFACE = 'tarmac'

    # DATES maps event dates (used to build url in pyramid)
    # to joomla ids (where official results are stored)
    __DATES_BY_YEAR = defaultdict(list)

    def __init__(self, date):
        self._date = date

    @property
    def url(self):
        year = self._date[0:4]
        events = self.dates_by_year().get(year)
        if events:
            for date, event_name, _, __ in events:
                if date == self._date:
                    return f'{self.URL_BASE}/{year}/{event_name}/'
        raise ValueError(f'No event found for year {year} and date {self._date}')

    @classmethod
    def dates_by_year(cls):
        # XXX we are memoizing this, but we want to stop memoizing so we
        # can have an automated process load events hourly
        with cls.LOCK:
            if cls.__DATES_BY_YEAR:
                return cls.__DATES_BY_YEAR

            output = defaultdict(list)
            for filename in glob('archive/**/*.html'):
                year, date, event_name = cls.FILENAME_REGEX.search(filename).groups()
                surface = cls._surface(filename)
                friendly_date = cls._friendly_date(date)
                output[year].append((date, event_name, surface, friendly_date))

            for year, events in sorted(output.items(), reverse=True):
                cls.__DATES_BY_YEAR[year] = sorted(events, reverse=True)

            return cls.__DATES_BY_YEAR

    @classmethod
    def _surface(cls, filename):
        with open(filename, 'r') as ff:
            html = ff.read()
        if Shared.RALLYX_REGEX.search(html):
            return cls.DIRT_SURFACE

        return cls.TARMAC_SURFACE

    @classmethod
    def _friendly_date(cls, date_string):
        if not len(date_string) == 10:
            raise AssertionError
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%b&nbsp;%d')


if __name__ == '__main__':
    import requests

    HOST = 'http://localhost:6543'
    # HOST = 'http://arscca.jackdesert.com'
    dates = PublishedEvent.dates_by_year()

    for date, event_name in PublishedEvent.dates_by_year().items():
        url = f'{HOST}/events/{date}?cb=1'
        print(f'Parsing {date}')

        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            print(f'ERROR: {url}')
