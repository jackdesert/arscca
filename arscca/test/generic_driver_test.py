import unittest
import pytest
import pdb

from arscca.models.driver import GenericDriver

from decimal import Decimal
from pyramid import testing
from unittest.mock import patch


# We don't instantiate the GenericDriver class in the app,
# but since it hold shared functionality, we use it in testing.

class GenericDriverTest(unittest.TestCase):
    def test__name(self):
        driver = GenericDriver(1942,
                               ['a', 'b', 'c', 'dain', 'e'],
                               None,
                               5,
                               13)
        self.assertEqual(driver.name, 'Dain')

    def test__car_class(self):
        driver = GenericDriver(1942,
                               ['a', 'ss', 'c'],
                               None,
                               5,
                               13)
        self.assertEqual(driver.car_class, 'ss')

    def test__car_number(self):
        driver = GenericDriver(1942,
                               ['a', 'ss', '16'],
                               None,
                               5,
                               13)
        self.assertEqual(driver.car_number, '16')

    def test__car_model(self):
        driver = GenericDriver(1942,
                               ['a', 'ss', '16', 'Pam', 'BMW'],
                               None,
                               5,
                               13)
        self.assertEqual(driver.car_model, 'BMW')

    # TODO mock/patch GenericDriver.slug
    def test__id(self):
        driver = GenericDriver(1942,
                               ['some_number', 'ss', '16', 'Georgia Brown'],
                               None,
                               5,
                               13)
        self.assertEqual(driver.id, 'georgia_brown--ss_16')

    # TODO mock/patch Canon.slug
    def test__driver_slug(self):
        driver = GenericDriver(1942,
                               ['some_number', 'ss', '16', 'Georgia Brown'],
                               None,
                               5,
                               13)
        self.assertEqual(driver.driver_slug, 'georgia_brown')

    # WHY AM I TESTING PRIVATE METHODS?
    # Whether the end user needs access to a particular method is a separate
    # question from whether the method offers an insightful view
    # into whether data is flowing correctly.
    #
    # If it offers an insightful view, I see value in testing it.
    # If the end user doesn't actually call the method, no need to make
    # it public.
    #
    # So hence some private methods are being tested.
    # Feel free to change up the tests as the implementation changes.


    # When two rows per driver and first_run_column is 7
    # _runs upper will start at index 7 and go to second to last column
    # See comments at the top of LogSplitter
    def test__runs_upper___and__runs_lower_1(self):
        driver = GenericDriver(None,
                               ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'),
                               ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',  'k'),
                               7,
                               10)
        self.assertEqual(driver._runs_upper(), ('7', '8', '9'))
        self.assertEqual(driver._runs_lower(), ('h', 'i', 'j'))

    # When one row per driver and first_run_column is 5
    # _runs upper will start at index 5 and go to third to last column
    # See comments at the top of LogSplitter
    def test__runs_upper___and__runs_lower_2(self):
        driver = GenericDriver(None,
                               ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'),
                               None,
                               5,
                               9)
        self.assertEqual(driver._runs_upper(), ('5', '6', '7', '8'))
        self.assertEqual(driver._runs_lower(), tuple())


    def test__best_of_n(self):
        driver = GenericDriver(None, None, None, None, None)
        data = {('1', '2', '3'): Decimal('1'),
                ('', '1'): Decimal('1'),
                (' ', '1'): Decimal('1'),
                ('', ' '): None,
                ('1.5+1', '2.5'): Decimal('2.5'),
                ('1.5+2', '1300'): Decimal('5.5')
               }
        for inputs, best in data.items():
            self.assertEqual(best, driver._best_of_n(inputs))

    def test__penalty_from_pylons(self):
        data = {'1': 2,
                '2': 4}
        driver = GenericDriver(None, None, None, None, None)
        for pylon_count, penalty_in_seconds in data.items():
            self.assertEqual(driver._penalty_from_pylons(pylon_count), penalty_in_seconds)

    def test_time_from_string(self):
        data = {'36': Decimal('36'),
                '42.334+2': Decimal('46.334'),
                '40+2/1': Decimal('54.000'), # One missed gate
                '40+1/0': Decimal('42.000'), # Zero missed gates
                '90+': Decimal('90'),
                '90+ ': Decimal('90'),
                '30+dnf': GenericDriver.INF,
                '30+dns': GenericDriver.INF}
        driver = GenericDriver(None, None, None, None, None)

        for string, time in data.items():
            self.assertEqual(driver.time_from_string(string), time)

    @patch('arscca.models.driver.GenericDriver._runs_upper', return_value=('6', '5', 'DNF', ' '))
    def test_num_completed_runs_upper(self, runs):
        driver = GenericDriver(None, None, None, None, None)
        self.assertEqual(driver.num_completed_runs_upper(), 3)

    @patch('arscca.models.driver.GenericDriver._runs_lower', return_value=('6', '5', '', ' '))
    def test_num_completed_runs_lower(self, runs):
        driver = GenericDriver(None, None, None, None, None)
        self.assertEqual(driver.num_completed_runs_lower(), 2)


