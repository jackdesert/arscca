'''
This module pulls events from arscca.org and writes them
to disk inside this repository.
'''
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup, Comment

from singleton import file_based_singleton

PARENT_DIR = 'Parent Directory'
BASE_URL = 'http://arscca.org/event_results'
NUM_RETRIES = 5
RETRY_DELAY_SECONDS = 1
TIMEOUT_SECONDS = 10

# Events before 2009 have a different layout and would require additional effort to parse
MINIMUM_YEAR = '2009'

# Note these all start with http...these are hosted on https, so ideally
# we would canonize
SKIPPED_EVENT_URLS = frozenset(['http://arscca.org/event_results/2019/TnT/', # Odd formatting (TNT)
    'http://arscca.org/event_results/2020/RallyX-Event1/', # Only a partial file
    'http://arscca.org/event_results/2007/Event1/', # pdf

    ])

#def temp_write(html):
#    """
#    Dev helper for writing html to viewable location
#    """
#    fname = '/tmp/event.html'
#    with open(fname, 'w') as writer:
#        print(f'Writing to {fname}')
#        writer.write(html)

class FinalEventNotFound(Exception):
    """
    Raised when "final" event not found on page where event expected
    """

def _td_with_class_indexcolname(soup):
    return soup('td', 'indexcolname')

def loop_get(url):
    # This function retries your requests.get if it times out
    for index in range(NUM_RETRIES):
        try:
            return requests.get(url, timeout=TIMEOUT_SECONDS)
        except Exception as eee:
            if not isinstance(eee, requests.RequestException):
                raise eee
            sleep(RETRY_DELAY_SECONDS)
            print(f'{index}. RETRYING {url} because {eee} where timeout={TIMEOUT_SECONDS}s')
    raise RuntimeError(f'Failed after {NUM_RETRIES} tries fetching {url} when timeout={TIMEOUT_SECONDS}s')

class TopLevelFetcher:
    YEAR_REGEX = re.compile(r'\d{4}')

    def __init__(self, url):
        self._url = url

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
        year_fetchers = []
        for td in _td_with_class_indexcolname(soup):
            for link in td('a'):
                if link.text == PARENT_DIR:
                    continue
                search = self.YEAR_REGEX.search(link.text)
                assert search
                year = search[0]
                href = link['href']

                if year >= MINIMUM_YEAR and (year == precise_year or precise_year is None):
                    year_fetcher = YearFetcher(year, href)
                    year_fetchers.append(year_fetcher)
        return year_fetchers


class YearFetcher:

    def __init__(self, year, path):
        self._year = year
        self._path = path

    def locate_events(self):
        print('YearFetcher.locate_events')
        url = f'{BASE_URL}/{self._path}'

        req = loop_get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        event_fetchers = []
        for td in _td_with_class_indexcolname(soup):
            for link in td('a'):
                if link.text == PARENT_DIR:
                    continue
                href = link['href']
                event_fetcher = EventFetcher(self._year, href)
                event_fetchers.append(event_fetcher)
        if not event_fetchers:
            print(f'NO EVENTS FOR {self._year}')
        return event_fetchers

class EventFetcher:
    BASE_URL = 'http://arscca.org'
    # Rallyx sometimes has _fin.htm instead of _fin_.htm
    FINAL_FILENAME_REGEX = re.compile(r'(-|_)fin(al)?_?\.html?$')

    __slots__ = ('_year', '_path')
    def __init__(self, year, path):
        self._year = year
        self._path = path

    def locate_results(self):
        print('EventFetcher.locate_results')
        url = f'{BASE_URL}/{self._year}/{self._path}'
        if 'season' in self._path:
            return None
        if url in SKIPPED_EVENT_URLS:
            return None
        print(url)

        req = loop_get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        # Some years use list-title, other years use item-title
        # The indexcolname holds the filenames
        for td in _td_with_class_indexcolname(soup):
            for link in td('a'):
                # Only grab the one that is a "final" file
                if self.FINAL_FILENAME_REGEX.search(link.text.strip()):
                    href = link['href']
                    # Sometimes url has trailing slash already
                    url = url.rstrip('/')
                    event_url = f'{url}/{href}'
                    return FinalFetcher(year=self._year, event_name=self._path, event_url=event_url)
        msg = f'No event found at url {url}'
        print(f'\n\n********************\n {msg}\n')
        raise FinalEventNotFound(msg)

# XXX Rename to EventFetcher (the other is EventFinder or EventLocator)
class FinalFetcher:
    """
    Takes a single event and writes it to disk
    """
    MONTH_FIRST_DATE_REGEX = re.compile(r'(\d\d)-(\d\d)-(\d\d\d\d)')

    # Matching on html comment:
    #    <!-- Date Created: Sun Jun 16 21:37:29 2019 -->
    # Note this is the date the report was generated, not the day of the event.
    # (This is only used as a backup in case MONTH_FIRST_DATE_REGEX is not found)
    DATE_IN_COMMENTS_REGEX = re.compile(r'Date Created: \S{3} (\S{3}) (\d{1,2}).*(\d{4})')

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

        with open(self._filename, 'w', encoding='utf8') as ff:
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

    import pytz

    tz = pytz.timezone('America/Chicago')
    chicago_now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %z')
    print(f'Fetched at {chicago_now}')

    PRECISE_YEAR = None
    if len(sys.argv) > 1:
        PRECISE_YEAR = sys.argv[1]
        print(f'Fetching only for year {PRECISE_YEAR}')
    if PRECISE_YEAR is not None and not re.compile(r'^\d{4}$').search(PRECISE_YEAR):
        # Make sure an actual year is passed in, because in cron generating the year is tricky
        raise ValueError('PRECISE_YEAR must be decimal')

    # Use a file based singleton so that when this is called by cron,
    # long-running processes will not pile up
    with file_based_singleton('/tmp/archive-events-singleton-dir'):
        FinalFetcher.stats()
        top_fetcher = TopLevelFetcher(f'{BASE_URL}#iframe-buster')
        year_fetchers_ = top_fetcher.locate_years(PRECISE_YEAR)

        for year_fetcher_ in year_fetchers_:
            event_fetchers_ = year_fetcher_.locate_events()
            for event_fetcher_ in event_fetchers_:
                final_fetcher = event_fetcher_.locate_results()
                if final_fetcher is not None:
                    final_fetcher.archive_event()



