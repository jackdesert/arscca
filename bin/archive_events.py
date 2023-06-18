'''
This module pulls events from arscca.org and writes them
to disk inside this repository.
'''
from bs4 import BeautifulSoup
from bs4 import Comment
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import pdb
import re
import requests

PARENT_DIR = 'Parent Directory'
BASE_URL = 'http://arscca.org/event_results'

class FinalEventNotFound(Exception):
    """
    Raised when "final" event not found on page where event expected
    """

def _td_with_class_indexcolname(soup):
    return soup('td', 'indexcolname')

def loop_get(url):
    # This function retries your requests.get if it times out
    req = None
    while not req:
        try:
            req = requests.get(url, timeout=1)
        except Exception as eee:
            if not isinstance(eee, requests.RequestException):
                raise eee
            print(f'RETRYING {url}')
    return req

class TopLevelFetcher:
    YEAR_REGEX = re.compile('\d{4}')

    def __init__(self, url):
        self._url = url
        self._year_fetchers = []

    def locate_years(self, precise_year=None):
        '''
        Locate years on page and call locate_events() for each year.
        :param precise_year: Integer value that limits years to only that year.
        '''
        print('TopLevelFetcher.locate_years')
        req = loop_get(self._url)
        soup = BeautifulSoup(req.text, 'lxml')
        # Find td elements with class indexcolname
        # Used to be reversed
        for td in _td_with_class_indexcolname(soup):
            for link in td('a'):
                if link.text == PARENT_DIR:
                    continue
                search = self.YEAR_REGEX.search(link.text)
                assert search
                year = search[0]
                href = link['href']

                if (year == precise_year) or precise_year is None:
                    year_fetcher = YearFetcher(year, href)
                    self._year_fetchers.append(year_fetcher)
                    year_fetcher.locate_events()


class YearFetcher:

    def __init__(self, year, path):
        self._year = year
        self._path = path
        self._event_fetchers = []

    def locate_events(self):
        print('YearFetcher.locate_events')
        url = f'{BASE_URL}/{self._path}'

        req = loop_get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        found = False
        for td in _td_with_class_indexcolname(soup):
            found = True
            for link in td('a'):
                if link.text == PARENT_DIR:
                    continue
                href = link['href']
                event_fetcher = EventFetcher(self._year, href)
                self._event_fetchers.append(event_fetcher)
                event_fetcher.locate_results()
        if not found:
            print(f'NO EVENTS FOR {self._year}')

class EventFetcher:
    BASE_URL = 'http://arscca.org'

    def __init__(self, year, path):
        self._year = year
        self._path = path
        self._final_fetchers = []

    def locate_results(self):
        print('EventFetcher.locate_results')
        url = f'{BASE_URL}/{self._year}/{self._path}'
        print(url)

        req = loop_get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        # Some years use list-title, other years use item-title
        for td in _td_with_class_indexcolname(soup):
            for link in td('a'):
                if link.text.strip().endswith('_fin_.htm'):
                    href = link['href']
                    event_url = f'{url}/{href}'
                    final_fetcher = FinalFetcher(year=self._year, event_name=self._path, event_url=event_url)
                    self._final_fetchers.append(final_fetcher)
                    final_fetcher.archive_event()
                    return
        msg = f'No event found at url {url}'
        raise FinalEventNotFound(msg)

# XXX Rename to EventFetcher (the other is EventFinder or EventLocator)
class FinalFetcher:
    """
    Takes a single event and writes it to disk
    """
    MONTH_FIRST_DATE_REGEX = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')

    # Matching on html comment:
    #    <!-- Date Created: Sun Jun 16 21:37:29 2019 -->
    # Note this is the date the report was generated, not the day of the event.
    # (This is only used as a backup in case MONTH_FIRST_DATE_REGEX is not found)
    DATE_IN_COMMENTS_REGEX = re.compile('Date Created: \S{3} (\S{3}) (\d{1,2}).*(\d{4})')

    OUTPUT_DIR = 'archive'
    FRIENDLY_DATE_FORMAT = '%b %d %Y'
    STANDARD_DATE_FORMAT = '%Y-%m-%d'

    NON_SLUG_CHARS_REGEX = re.compile(r'[^a-zA-Z0-9-_]')

    CRLF = '\r\n'
    LF = '\n'

    # Keep a log of all events fetched
    LOG = []

    __slots__ = ('_year', '_event_url', '_event_name', '_date', '_html',)
    def __init__(self, *, year, event_name, event_url):
        self._year = year
        self._event_url = event_url
        # Make sure event name has no spaces
        self._event_name = self.NON_SLUG_CHARS_REGEX.sub('-', event_name.strip('/'))
        self._date = None
        self._html = None

    def archive_event(self):
        self._store_html_and_date()
        assert self._date
        assert self._year

        # Make sure the year we parsed in the final results
        # matches the year from the originating category link
        assert self._year == self._date[0:4]
        self._write_to_disk()


    def _write_to_disk(self):
        assert self._html

        print(f'Writing {self._filename}')

        with open(self._filename, 'w') as ff:
            ff.write(self._html)
        self.LOG.append((self._date, self._event_name))


    @property
    def _filename(self):
        dir_ = f'{self.OUTPUT_DIR}/{self._year}'
        # Ensure dir_ exists
        Path(dir_).mkdir(exist_ok=True)
        assert self._date

        return f'{dir_}/{self._date}__{self._event_name}.html'

    def _store_html_and_date(self):
        req = loop_get(self._event_url)

        self._html = req.text.replace(self.CRLF, self.LF)

        soup = BeautifulSoup(self._html, 'lxml')
        for th in soup('th'):
            search = self.MONTH_FIRST_DATE_REGEX.search(th.text)
            if search:
                month = search[1]
                day = search[2]
                year = search[3]
                self._date = f'{year}-{month}-{day}'
                return

        comment_soup = BeautifulSoup(req.content.decode(), 'lxml')
        # See https://stackoverflow.com/questions/33138937/
        comments = comment_soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            search = self.DATE_IN_COMMENTS_REGEX.search(comment)
            if search:
                month_name = search[1]
                day = search[2]
                year = search[3]
                friendly_string = f'{month_name} {day} {year}'
                date_object = datetime.strptime(friendly_string, self.FRIENDLY_DATE_FORMAT)
                self._date = date_object.strftime(self.STANDARD_DATE_FORMAT)
                return

        raise RuntimeError('Expected to find a date either in a th or in a comment')

    @classmethod
    def stats(cls):
        print(f'{len(cls.LOG)} events')
        dates = defaultdict(int)
        joomla_ids = defaultdict(int)
        for date, joomla_id in cls.LOG:
            dates[date] += 1
            joomla_ids[joomla_id] += 1
        duplicate_dates = [date for date, count in dates.items() if count > 1]
        duplicate_joomla_ids = [jid for jid, count in joomla_ids.items() if count > 1]
        print(f'duplicate dates: {duplicate_dates}')
        if duplicate_dates:
            print('To fix duplicated dates, manually edit the "Created At" comment in joomla, then run this again')
        print(f'duplicate joomla_ids: {duplicate_joomla_ids}')

if __name__ == '__main__':

    import sys
    precise_year = None
    if len(sys.argv) > 1:
        precise_year = sys.argv[1]

    FinalFetcher.stats()
    top = TopLevelFetcher(f'{BASE_URL}#iframe-buster')
    top.locate_years(precise_year)

    FinalFetcher.stats()



