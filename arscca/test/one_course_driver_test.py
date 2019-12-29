import unittest
import pytest
import pdb

from arscca.models.driver import OneCourseDriver

from decimal import Decimal
from pyramid import testing
from unittest.mock import patch


class OneCourseDriverTest(unittest.TestCase):

    @patch('arscca.models.driver.OneCourseDriver._runs_upper', return_value=('25',))
    @patch('arscca.models.driver.OneCourseDriver._runs_lower', return_value=(tuple()))
    def test_best_run(self, _runs_upper, _runs_lower):
        driver = OneCourseDriver(None, None, None, None, None)
        self.assertEqual(driver.best_run(), Decimal('25'))

    @patch('arscca.models.driver.OneCourseDriver.best_run', return_value=Decimal('30'))
    @patch('arscca.models.driver.OneCourseDriver.pax_factor', return_value=(Decimal('0.9')))
    def test_best_run_pax(self, best_run, pax_factor):
        driver = OneCourseDriver(None, ('0', '1', '2', '3'), None, None, None)
        self.assertEqual(driver.best_run_pax(), Decimal('27'))


    # Do we need a test for OneCourseDriver.properties??
