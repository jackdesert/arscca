from bs4 import BeautifulSoup
from bs4 import Comment
from datetime import datetime
import pdb
import re
import requests

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

    def locate_years(self):
        req = loop_get(self._url)
        soup = BeautifulSoup(req.text, 'lxml')
        for h3 in soup('h3'):
            for link in h3('a'):
                search = self.YEAR_REGEX.search(link.text)
                assert search
                year = search[0]
                href = link['href']

                year_fetcher = YearFetcher(year, href)
                self._year_fetchers.append(year_fetcher)
                year_fetcher.locate_events()

class YearFetcher:
    BASE_URL = 'http://arscca.org'

    def __init__(self, year, path):
        self._year = year
        self._path = path
        self._event_fetchers = []

    def locate_events(self):
        url = f'{self.BASE_URL}/{self._path}'

        req = loop_get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        found = False
        for h3 in soup('h3'):
            found = True
            for link in h3('a'):
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
        url = f'{self.BASE_URL}/{self._path}'

        req = loop_get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        # Some years use list-title, other years use item-title
        for td in soup('td', ['list-title', 'item-title']):
            for link in td('a'):
                if 'Final' in link.text:
                    href = link['href']
                    final_fetcher = FinalFetcher(self._year, href)
                    self._final_fetchers.append(final_fetcher)
                    final_fetcher.archive_event()

class FinalFetcher:
    BASE_URL = 'http://arscca.org'
    MONTH_FIRST_DATE_REGEX = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')

    # Matching on html comment:
    #    <!-- Date Created: Sun Jun 16 21:37:29 2019 -->
    DATE_IN_COMMENTS_REGEX = re.compile('Date Created: \S{3} (\S{3}) (\d{1,2}).*(\d{4})')

    OUTPUT_DIR = 'archive'
    FRIENDLY_DATE_FORMAT = '%b %d %Y'
    STANDARD_DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, year, path):
        self._year = year
        self._path = path
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


    @property
    def _filename(self):
        assert self._date

        return f'{self.OUTPUT_DIR}/{self._date}.html'

    def _store_html_and_date(self):
        url = f'{self.BASE_URL}/{self._path}'

        req = loop_get(url)

        self._html = req.text

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

        pdb.set_trace()
        #raise RuntimeError('Expected to find a date either in a th or in a comment')


if __name__ == '__main__':

    top = TopLevelFetcher('http://arscca.org/index.php?option=com_content&view=category&id=8&Itemid=104')
    top.locate_years()




