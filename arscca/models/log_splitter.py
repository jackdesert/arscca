"""
The log splitter determines driver type

See _set_driver_type()
"""
from arscca.models.driver import AsphaltRallyDriver
from arscca.models.driver import OneCourseDriver
from arscca.models.driver import RallyDriver
from arscca.models.driver import TwoCourseDriver
from arscca.models.event_helper import AsphaltRallyEventHelper
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

import logging
LOG = logging.getLogger('arscca')
FUNKY_ENCODED_NBSP = 'Â\xa0'

# Some rallyx dates are hardcoded because they did not match expected patterns
HARDCODED_RALLYX_DATES = (
        '2019-04-13', # Funky html
        '2018-11-02',
        )

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

    FIRST_RUN_COLUMN_HEADER_REGEX = re.compile(r'Times|Runs|Run 1')

    # This filename ends in jinja2 because it is used as a view template
    LIVE_FILENAME = '/home/arscca/arscca-live.jinja2'
    DATE_REGEX = re.compile(r'(\d\d)-(\d\d)-(\d\d\d\d)')
    PRIMARY_PUBLISHED_SCORE_COLUMN_REGEX = re.compile(r'Total')

    def __init__(self, date, url, live, local_html_file=None):
        self.date = date
        self.url = url
        self.live = live  # Boolean

        self._local_html_file = local_html_file
        self._point_storage = defaultdict(int)
        self.driver_type = None
        self._results_table = None
        self._first_run_column = None
        self._primary_published_score_column = None
        self._data = None
        self._num_rows_per_driver = None
        self.html = None

    def build_and_return_drivers(self):
        self._load_soup()
        self._load_results_table()
        self._load_row_groups()
        self._num_rows_per_driver = self._infer_num_rows_per_driver()

        self._set_driver_type()
        return self._build_drivers_from_row_groups()

    @property
    def event_helper(self):
        if self.driver_type == RallyDriver:
            return RallyEventHelper
        elif self.driver_type == AsphaltRallyDriver:
            return AsphaltRallyEventHelper
        elif self.driver_type == OneCourseDriver:
            return OneCourseEventHelper
        elif self.driver_type == TwoCourseDriver:
            return TwoCourseEventHelper
        raise RuntimeError('Incorrect Driver Type')

    @property
    def event_name(self):
        if self.live:
            return f'Live Results {self.date}'
        return self._local_html_file.split('__', 1)[1].split('.')[0]

    def _load_soup(self):
        fname = self.LIVE_FILENAME if self.live else self._local_html_file
        with open(fname, encoding='utf8') as reader:
            html = reader.read()


        # Funky Encodings
        # Somewhere along the way, it appears that we used the wrong encoding in our files.
        # Stripping out the 'Â' character from the html since we think in this pattern it
        # represents an &nbsp;
        # It appears to only occur as the only content inside an element. For example: <p>Â </p>
        # Note it's not a normal space after the Â...if you put it inside a python string it will
        # show up as a yellow underscore....that's why it uses the \x notation in FUNKY_ENCODED_NBSP
        # See https://stackoverflow.com/questions/1461907/html-encoding-issues-%C3%82-character-showing-up-instead-of-nbsp
        self.html = html.replace(f'>{FUNKY_ENCODED_NBSP}<', '> <')

        self._soup = BeautifulSoup(self.html, 'html.parser')


    def _load_results_table(self):

        # First table has the event name and date
        date_table = self._soup('table')[
            0
        ]  # Failure here means file is empty; check twisted
        date_string = date_table('th')[0].text
        self.event_date = self.format_date(date_string)

        for table in self._soup('table'):
            self._first_run_column = None
            self._primary_published_score_column = None
            for tr in table('tr'):
                index = 0
                for th in tr('th'):
                    # Two types of headers
                    # Standard headers: archive/2015-07-19.html
                    # Fancy headers: archive/2012-03-04.html
                    #
                    # If there's an indicator for first run column,
                    # then this is the correct table
                    #
                    # Note "Run 1" and "Run 10" both match "Run 1"
                    # so make sure you trip first_run_column on the
                    # first occurrenct
                    text = th.text.strip()
                    if (
                        self._first_run_column == None
                    ) and self.FIRST_RUN_COLUMN_HEADER_REGEX.match(text):
                        # Set the first run column
                        self._first_run_column = index

                    if self.PRIMARY_PUBLISHED_SCORE_COLUMN_REGEX.match(text):
                        self._primary_published_score_column = index

                    # Include colspan in index counting
                    index += int(th.get('colspan') or 1)

            if self._first_run_column and self._primary_published_score_column:
                self._results_table = table
                return

        raise RuntimeError(
            'No table found indicating both first run column and primary published score column'
        )

    def _load_row_groups(self):
        # Rows are grouped so that we always start with a primary row
        # meaning one that has a driver's name.
        #
        # Subsequent rows are sometimes useful

        groups = []
        for tr in self._results_table('tr'):
            if tr('a'):
                # Results from 2016 and earlier have two rows of class links
                # that we want to ignore.
                # BUT some events have hyperlinks in ALL THE BOXES ....
                continue
            # Note this skips header row if header is th
            row = [td.text for td in tr('td')]
            if self._start_row(row):
                # Create a new group
                group = [row]
                groups.append(group)
            elif self._useful_row(row):
                # Add this row to the last group
                groups[-1].append(row)
        self._row_groups = groups

    def _set_driver_type(self):


        # Note searching in html, not str(soup), since soup adds double quotes to `align=center`
        # and we want to match on the explicit axware output (assuming it is more accurate)
        if Shared.ASPHALT_RALLY_REGEX.search(self.html):
            # Note set up the event as single day if you want asphalt rally scoring
            # And also name the event with something in ASPHALT_RALLY_REGEX
            self.driver_type = AsphaltRallyDriver
            return

        if Shared.RALLYX_REGEX.search(self.html) or self.date in HARDCODED_RALLYX_DATES:
            self.driver_type = RallyDriver
            return

        d1 = 'D1'
        d2 = 'D2'
        rg = self._row_groups[0]

        if (self._num_rows_per_driver == 2) and d1 in rg[0] and d2 in rg[1]:
            if not rg[0].index(d1) == rg[1].index(d2):
                raise AssertionError
            self.driver_type = TwoCourseDriver
            return

        self.driver_type = OneCourseDriver

    def _infer_num_rows_per_driver(self):
        for group in self._row_groups:
            # If at least one groups has more than one (useful) row in it,
            if len(group) > 1:
                return 2
        return 1

    def _build_drivers_from_row_groups(self):
        year = self.date[0:4]
        drivers = []
        for row_group in self._row_groups:
            row_1 = tuple(row_group[0])
            if self._num_rows_per_driver == 1:
                row_2 = None
            elif (self._num_rows_per_driver == 2) and (len(row_group) > 1):
                row_2 = tuple(row_group[1])
            else:
                # Row with no useful data because driver requires a second row
                # but no useful row available
                row_2 = tuple(['' for item in row_1])

            driver = self.driver_type(
                year,
                row_1,
                row_2,
                self._first_run_column,
                self._primary_published_score_column,
            )
            drivers.append(driver)

        return drivers

    def format_date(self, string):
        matches = self.DATE_REGEX.search(string)
        if not matches:
            return string
        month = int(matches[1])
        day = int(matches[2])
        year = int(matches[3])
        date = Date(year, month, day)
        return date.strftime('%B %-d, %Y')

    def _start_row(self, row):
        # Start rows must be useful
        if not self._useful_row(row):
            return False

        # A start row has a driver name
        for item in row[0:4]:
            if Shared.NOT_JUST_WHITESPACE_REGEX.search(item):
                return True

        return False

    def _useful_row(self, row):
        if not row:
            return False

        if len(row) < 6:
            # Events from 2016 and earlier include a summary at the
            # bottom of the table. The summary is only five cols wide.
            return False

        # A useful row as either Name, car, etc
        # OR it has D1|D2 in row[6]
        # OR in the case of one-course-drivers with two rows per driver,
        # it has a time in row[6]
        for item in row[0:7]:
            if Shared.NOT_JUST_WHITESPACE_REGEX.search(item):
                return True

        return False
