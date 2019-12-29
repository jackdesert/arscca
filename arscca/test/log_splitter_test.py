from arscca.models.driver import GenericDriver
from arscca.models.driver import OneCourseDriver
from arscca.models.driver import RallyDriver
from arscca.models.driver import TwoCourseDriver
from arscca.models.log_splitter import LogSplitter
from glob import glob
import pdb
import re
import unittest

archive = (
    # FILENAME                  DRIVER_TYPE  NUM_ROWS_PER_DRIVER

    ('archive/2010-09-19__123.html', OneCourseDriver, 2), # Gov Cup 2010

    ('archive/2009-09-19__140.html', OneCourseDriver, 2), # Gov Cup 2009
    ('archive/2015-08-02__233.html', OneCourseDriver, 1), # Gov Cup 2015

    ('archive/2016-11-19__294.html', RallyDriver, 1),
    ('archive/2013-04-20__88.html', RallyDriver, 2),
    ('archive/2019-10-05__485.html', RallyDriver, 1),
    ('archive/2019-11-09__496.html', RallyDriver, 2),



    ('archive/2019-10-27__492.html', OneCourseDriver, 1), # Gov Cup 2019
    ('archive/2016-09-25__285.html', OneCourseDriver, 1), # Gov Cup 2016




)

DATE_REGEX = re.compile(r'archive/(.+)\.html')


# This is an integration test
class LogSplitterTest(unittest.TestCase):

    def test_build_and_return_drivers_1(self):
        # THIS IS AN INTEGRATION TEST
        # The primary goal is to verify that the correct driver_type is chosen
        # but other attributes will also be inspected
        for filename, driver_type, num_rows_per_driver in archive:
            print(f'{filename} (with assertions)')
            date = DATE_REGEX.match(filename)[1]
            splitter = LogSplitter(date,
                                   f'fake-url-for-{date}',
                                   False,
                                   local_html_file=filename)


            drivers = splitter.build_and_return_drivers()

            # If there is no _data, it probably missed the table
            assert splitter._row_groups

            assert splitter._num_rows_per_driver == num_rows_per_driver
            driver = drivers[0]
            assert isinstance(driver, driver_type)

    def test_build_and_return_drivers_2(self):
        # THIS IS AN INTEGRATION TEST

        #for filename in sorted(glob('archive/*.html')):
        for filename in ['archive/2019-10-13__488.html']:
            print(f'{filename} (render only)')
            date = DATE_REGEX.match(filename)[1]
            splitter = LogSplitter(date,
                                   f'fake-url-for-{date}',
                                   False,
                                   local_html_file=filename)


            drivers = splitter.build_and_return_drivers()

            # If there is no _data, it probably missed the table
            assert splitter._row_groups

            pdb.set_trace()
            for driver in drivers:
                assert isinstance(driver, GenericDriver)

                # Manually set second_half_started because usually
                # Dispatcher would do so
                driver.second_half_started = True

                # Make sure nothing breaks when computing scores
                driver.primary_score()
                driver.secondary_score()

                # Make sure we have not accidentally used a blank row to create
                # My first choice was to assert on driver.name
                # But this event has a driver with no name:
                # archive/2009-09-19.html
                if not (driver.name.strip() or driver.car_class.strip()):
                    pdb.set_trace()

                assert driver.name.strip() or driver.car_class.strip()
                assert driver.published_primary_score.strip()

