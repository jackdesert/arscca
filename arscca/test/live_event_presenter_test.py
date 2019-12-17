import unittest
import pytest
import pdb

from arscca.models.live_event_presenter import LiveEventPresenter

from pyramid import testing

class LiveEventPresenterTests(unittest.TestCase):
    def test_diff(self):

        previous_drivers = [{'name': 'Toledo', 'speed': 5},
                            {'name': 'Waltham', 'speed': 4},
                            {'name': 'Augusta', 'speed': 2}] # Augusta goes away

        drivers = [{'name': 'Toledo', 'speed': 15},           # Toledo changes
                   {'name': 'Waltham', 'speed': 4},          # Waltham stays the same
                   {'name': 'Cincinnati', 'speed': 15}]      # Cincinatti is new

        result = LiveEventPresenter.diff(previous_drivers, drivers)
        expected = {'create': ['Cincinnati'],
                    'destroy': ['Augusta'],
                    'update': [{'name': 'Toledo', 'speed': 15},     # Toledo Changed
                               {'name': 'Cincinnati', 'speed': 15}]}# Cincinnati is new

        self.assertEqual(result, expected)
