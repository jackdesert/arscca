import unittest
import pytest
import pdb

from arscca.models.histogram import Histogram

from pyramid import testing
from unittest.mock import patch

class HistogramTests(unittest.TestCase):
    # Note these tests do not actually exercise the locking mechanisms in the class
    def test__conformed_values(self):
        values = [10, 11, 15, 20, 22, 25]
        conformed_values, num_conformed = Histogram._conformed_values(values)
        expected = [10.0, 11.0, 15.0, 20.0, 20.0, 20.0]
        self.assertEqual(conformed_values, expected)
        self.assertEqual(num_conformed, 2)

    def test__bin_specification(self):
        min_value = 98
        max_value = 167
        num_values = 16
        width, quantity = Histogram._bin_specification(min_value, max_value, num_values)
        self.assertEqual(width, 10)
        self.assertEqual(quantity, 5)


    def test__bins_1(self):
        values = [99, 102, 112, 113, 110, 99, 101, 102, 102, 102, 102, 110]

        # Using a default bin width
        bins = Histogram._bins(values, 2)
        self.assertEqual(bins.tolist(), [98, 100, 102, 104, 106, 108, 110, 112, 114])

    def test__bins_2(self):
        values = [98, 102, 112, 114, 110, 99, 101, 102, 102, 102, 102, 110]

        # Using a default bin width
        bins = Histogram._bins(values, 2)
        self.assertEqual(bins.tolist(), [98, 100, 102, 104, 106, 108, 110, 112, 114, 116])


    @patch('arscca.models.histogram.Histogram._bin_specification', return_value=(4, 0))
    def test__bins_3(self, bin_spec):
        values = [98, 102, 112, 114, 110, 99, 101, 102, 102, 102, 102, 110]

        # Using a dynamic bin width, specified in the patch above
        bins = Histogram._bins(values, 0)
        self.assertEqual(bins.tolist(), [96, 100, 104, 108, 112, 116])


