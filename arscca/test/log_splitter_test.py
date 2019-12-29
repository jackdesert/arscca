from arscca.models.driver import OneCourseDriver
from arscca.models.driver import RallyDriver
from arscca.models.driver import TwoCourseDriver
from arscca.models.log_splitter import LogSplitter
import pdb
import re
import unittest

archive = (
    # FILENAME                  DRIVER_TYPE  NUM_ROWS_PER_DRIVER
    ('archive/2016-11-19.html', RallyDriver, 1),
    ('archive/2013-04-20.html', RallyDriver, 2),
    ('archive/2019-10-05.html', RallyDriver, 1),
    ('archive/2019-11-09.html', RallyDriver, 2),
)

DATE_REGEX = re.compile(r'archive/(.+)\.html')


# This is an integration test
class LogSplitterTest(unittest.TestCase):

    def test_build_and_return_drivers(self):
        # THIS IS AN INTEGRATION TEST
        # The primary goal is to verify that the correct driver_type is chosen
        # but other attributes will also be inspected
        for filename, driver_type, num_rows_per_driver in archive:
            date = DATE_REGEX.match(filename)[1]
            splitter = LogSplitter(date,
                                   f'fake-url-for-{date}',
                                   False,
                                   local_html_file=filename)


            drivers = splitter.build_and_return_drivers()

            # If there is no _data, it probably missed the table
            assert splitter._data

            assert splitter._num_rows_per_driver == num_rows_per_driver
            driver = drivers[0]
            assert isinstance(driver, driver_type)


