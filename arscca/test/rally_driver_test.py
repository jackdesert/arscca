import unittest
import pytest
import pdb

from arscca.models.driver import RallyDriver

from decimal import Decimal
from pyramid import testing
from unittest.mock import patch


class RallyDriverTest(unittest.TestCase):


    def cumulative(self):
        runs = [run for run in self.runs() if run.strip()]
        score = sum([self.time_from_string(run) for run in runs])
        if not score:
            return self.INF
        return score


    @patch('arscca.models.driver.RallyDriver.runs', return_value=('3','5', '7'))
    def test_cumulative_1(self, runs):
        driver = RallyDriver(None, None, None, None, None)
        self.assertEqual(driver.cumulative(), Decimal('15'))

    # with a blank run
    @patch('arscca.models.driver.RallyDriver.runs', return_value=('3','5', '7', ''))
    def test_cumulative_2(self, runs):
        driver = RallyDriver(None, None, None, None, None)
        self.assertEqual(driver.cumulative(), Decimal('15'))

    # with a DNF
    @patch('arscca.models.driver.RallyDriver.runs', return_value=('3','5', 'DNF', ''))
    def test_cumulative_3(self, runs):
        driver = RallyDriver(None, None, None, None, None)
        self.assertEqual(driver.cumulative(), RallyDriver.INF)


    # Do we need a test for RallyDriver.properties??
