from arscca.models.driver import OneCourseDriver
from arscca.models.driver import RallyDriver
from arscca.models.driver import TwoCourseDriver
from arscca.models.event_helper import OneCourseEventHelper
from arscca.models.event_helper import RallyEventHelper
from arscca.models.event_helper import TwoCourseEventHelper
from arscca.models.shared import Shared
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import date as Date
import pdb
import re
import requests


# VARIATIONS
# Events with two rows per driver use the last column as published score
# When only one row per driver, the second to last column is published score.
# The other way to detect this is by inspecting the column headings
# The various Driver classes infer which column to use by whether _row_2 is None
#
# Two course events have a column header called "Day" will cells D1 / D2
# One course events have no such column
#
# Rally Events have a thing right on the page that says RallyX
#




class LogSplitter:

    FIRST_RUN_COLUMN_HEADER_REGEX = re.compile('Times|Runs|Run 1')

    # This filename ends in jinja2 because it is used as a view template
    LIVE_FILENAME = '/home/arscca/arscca-live.jinja2'
    DATE_REGEX = re.compile('(\d\d)-(\d\d)-(\d\d\d\d)')


    def __init__(self, date, url, live, local_html_file=None):
        self.date = date
        self.url = url
        self.live = live # Boolean

        # pass in a local_html_file for testing
        self._local_html_file = local_html_file
        self._point_storage = defaultdict(int)
        self.driver_type = None
        self._results_table = None
        # self.drivers will be an array
        # self.table_width with be an integer
        # self.event_name will be a string
        # self.data will be a list
        # self._first_run_column will be an integer

    def build_and_return_drivers(self):
        self._load_soup()
        self._load_results_table()
        self._load_data()

        self._set_event_details()
        self._choose_driver_type()
        self._num_rows_per_driver = self._infer_num_rows_per_driver()
        return self._build_drivers_from_compiled_data()


    @property
    def event_helper(self):
        if self.driver_type == RallyDriver:
            return RallyEventHelper
        elif self.driver_type == OneCourseDriver:
            return OneCourseEventHelper
        elif self.driver_type == TwoCourseDriver:
            return TwoCourseEventHelper


    def _load_soup(self):
        if self.live:
            with open(self.LIVE_FILENAME, 'r') as ff:
                html = ff.read()
        elif self._local_html_file:
            # This path is used with the test suite
            with open(self._local_html_file, 'r') as ff:
                html = ff.read()
        else:
            rr = requests.get(self.url, allow_redirects=False, timeout=10)
            html = rr.text

        self._soup = BeautifulSoup(html, 'html.parser')

    def _set_event_details(self):
        if 'RallyX Mode' in self._soup.text:
            self.driver_type = RallyDriver


        if self.live:
            self.event_name = f'Live Results {self.date}'
        else:
            # First h2 has title
            self.event_name = self._soup.find('h2').text.strip().replace('Final', '')


        header_row = self._results_table('tr')[0]
        self._first_run_column = self._infer_first_run_column(header_row)

    def _load_results_table(self):

        # First table has the event name and date
        date_table = self._soup('table')[0] # Failure here means file is empty; check twisted
        date_string = date_table('th')[0].text
        self.event_date = self.format_date(date_string)

        for table in self._soup('table'):
            for tr in table('tr'):
                for th in tr('th'):
                    # Two types of headers
                    # Standard headers: archive/2015-07-19.html
                    # Fancy headers: archive/2012-03-04.html
                    if th.text == 'Times':
                        self._results_table = table
                        return

        raise RuntimeError('No table found with th with text Driver')

    def _load_data(self):

        data = []
        for tr in self._results_table('tr'):
            if tr('a'):
                # Results from 2016 and earlier have two rows of class links
                # that we want to ignore.
                continue
            # Note this skips header row if header is th
            row = [td.text for td in tr('td')]
            if row and self._useful_row(row):
                data.append(row)
        self._data = data

    def _infer_first_run_column(self, header_row):
        ths = [th.text for th in header_row('th')]
        for index, value in enumerate(ths):
            if self.FIRST_RUN_COLUMN_HEADER_REGEX.search(value):
                return index
        raise RuntimeError('No header to indicate first run column')

    def _choose_driver_type(self):
        # This method decides which parser to use for the event
        if self.driver_type == RallyDriver:
            # This was set in a previous method based on html on the page
            return

        d1 = 'D1'
        d2 = 'D2'

        if d1 in self._data[0] and d2 in self._data[1]:
            assert self._data[0].index(d1) == self._data[1].index(d2)
            self.driver_type = TwoCourseDriver

        else:
            self.driver_type = OneCourseDriver

    def _infer_num_rows_per_driver(self):

        assert self._data

        if self.driver_type == TwoCourseDriver:
            return 2

        # If a useful row has data in any of the first five columns,
        # it is a new driver
        for item in self._data[1][0:5]:
            if Shared.NOT_JUST_WHITESPACE_REGEX.match(item):
                return 1

        # A useful row with values in all of the first five columns
        # comprises a driver
        if all(map(lambda x : Shared.NOT_JUST_WHITESPACE_REGEX.match(x), self._data[1][0:5])):
            return 1

        # Otherwise it is runs for the driver in the row above
        return 2


    def _build_drivers_from_compiled_data(self):
        year = self.date[0:4]
        drivers = []
        for idx in range(0, len(self._data), self._num_rows_per_driver):
            row_1 = tuple(self._data[idx])
            row_2 = None
            if self._num_rows_per_driver == 2:
                row_2 = tuple(self._data[idx + 1])
            driver = self.driver_type(year, row_1, row_2, self._first_run_column)
            drivers.append(driver)

        return drivers

    def format_date(self, string):
        matches = self.DATE_REGEX.search(string)
        if not matches:
            return string
        month = int(matches[1])
        day   = int(matches[2])
        year  = int(matches[3])
        date  = Date(year, month, day)
        return date.strftime('%B %-d, %Y')

    def _useful_row(self, row):
        if len(row) < 6:
            # Events from 2016 and earlier include a summary at the
            # bottom of the table. The summary is only five cols wide.
            return False

        # A useful row as either Name, car, etc
        # OR it has D1|D2 in row[6]
        for item in row[0:7]:
            if Shared.NOT_JUST_WHITESPACE_REGEX.match(item):
                return True

        return False

