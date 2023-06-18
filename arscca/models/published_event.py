from collections import defaultdict
from datetime import datetime
from glob import glob
import re

from arscca.models.shared import Shared


class PublishedEvent:
    # URL_BASE + id maps to the location of FINAL results
    # Required params: ['com_content', 'view', 'id']
    URL_BASE = 'http://arscca.org/event_results'
    FILENAME_REGEX = re.compile(r'/(\d{4})/(.+)__(.+)\.html')

    DIRT_SURFACE = 'dirt'
    TARMAC_SURFACE = 'tarmac'


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

        intermediate = defaultdict(list)
        for filename in glob('archive/**/*.html'):
            year, date, event_name = cls.FILENAME_REGEX.search(filename).groups()
            surface = cls._surface(filename)
            friendly_date = cls._friendly_date(date)
            intermediate[year].append((date, event_name, surface, friendly_date))

        output = defaultdict(list)
        for year, events in sorted(intermediate.items(), reverse=True):
            output = sorted(events, reverse=True)

        return output

    @classmethod
    def _surface(cls, filename):
        with open(filename, encoding='utf-8') as ff:
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

    HOST_ = 'http://localhost:6543'
    # HOST = 'http://arscca.jackdesert.com'
    dates_ = PublishedEvent.dates_by_year()

    for date_, event_name_ in PublishedEvent.dates_by_year().items():
        url_ = f'{HOST_}/events/{date_}?cb=1'
        print(f'Parsing {date_}')

        res_ = requests.get(url_, timeout=10)
        if res_.status_code != 200:
            print(f'ERROR: {url_}')
