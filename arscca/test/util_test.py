import itertools
import pdb
import pytest
import unittest

from arscca.models.util import Util

from pyramid import testing

class UtilTests(unittest.TestCase):
    def test_range_with_skipped_values_1(self):
        result = Util.range_with_skipped_values(5, [2,3])
        self.assertEqual(result, [1, 4, 5, 6, 7])
    def test_range_with_skipped_values_2(self):
        result = Util.range_with_skipped_values(6, [1, 5])
        self.assertEqual(result, [2, 3, 4, 6, 7, 8])
    def test_range_with_skipped_values_3(self):
        # When a skipped value is larger than the biggest value
        result = Util.range_with_skipped_values(3, [1, 5])
        self.assertEqual(result, [2, 3, 4])
    def test_random_run_groups(self):
        data = {'as': ['George', 'Carla'],
                'bs': ['Amy'],
                'bsl': ['Claudia'],
                'cs': ['Barney', 'Samantha'],
                'ds': ['Jesus', 'Cepia', 'Pink'],
                'es': ['Frank', 'Elizabeth', 'Becki', 'Roosevelt'],
                'fs': ['Michele', 'Tara', 'Vicki'],
                'gs': ['Joan', 'Mia'],
                'jm': ['Fred']}
        # Run this multiple times, since the results are stochastic for large samples
        for i in range(7):
            groups, counter = Util.randomize_run_groups(data)
            for group in groups[0:2]:
                if 'bs' in group:
                    assert 'bsl' in group
            drivers_0 = list(itertools.chain(*groups[0].values()))
            drivers_1 = list(itertools.chain(*groups[1].values()))
            assert counter[0] == len(drivers_0)
            assert counter[1] == len(drivers_1)
            assert abs(len(drivers_0) - len(drivers_1)) < 3
            assert groups[2] == {'jm': ['Fred']}
