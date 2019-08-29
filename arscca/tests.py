import unittest
import pytest
import pdb

from arscca.models.canon import Canon
from arscca.models.driver import Driver
from arscca.models.gossip import Gossip
from arscca.models.live_event_presenter import LiveEventPresenter
from arscca.models.photo import Photo
from arscca.models.util import Util

from decimal import Decimal
from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from arscca.views.events import home_view
        request = testing.DummyRequest()
        info = home_view(request)
        self.assertTrue(isinstance(info['photos'], list))


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from arscca import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'Results' in res.body)

class PhotoTests(unittest.TestCase):
    def test_driver_slug(self):
        photo = Photo('first_last_torso')
        self.assertEqual('first_last', photo.driver_slug)

    def test_driver_slug_2(self):
        photo = Photo('first_last_car')
        self.assertEqual('first_last', photo.driver_slug)


    def test_all(self):
        assert Photo.all()

    def test_head_shots_memoized(self):
        memoized = Photo._head_shots_memoized()
        assert 'adam_cadorette' in memoized

    def test_head_shot(self):
        data = Photo.slug_and_head_shot('Adam., Cadorette')
        assert 'slug' in data
        assert 'head_shot' in data

    def test_head_shot_2(self):
        data = Photo.slug_and_head_shot('Barb Eldredge')
        assert 'slug' in data
        assert 'head_shot' in data

class GossipTests(unittest.TestCase):
    def test_html_when_file_not_exist(self):
        gossip = Gossip('unknown_driver_slug')
        with pytest.raises(FileNotFoundError):
            gossip.html(True)

    def test_all(self):
        # Verify that each file renders
        for gossip in Gossip.all():
            gossip.html(True)

class CanonTests(unittest.TestCase):
    def test_slug(self):
        data = {'Hi There'    : 'hi_there',
                ' Bona Fide ' : 'bona_fide',
                'Mr. Robinson': 'mr_robinson',
                'mr_tee'      : 'mr_tee'}

        for name_or_slug, expected_slug in data.items():
            slug = Canon(name_or_slug).slug
            self.assertEqual(slug, expected_slug)

    def test_name(self):
        data = {'Hi There'    : 'Hi There',
                ' Bona Fide ' : 'Bona Fide',
                'Mr. Robinson': 'Mr Robinson',
                'mr_tee'      : 'Mr Tee'}

        for name_or_slug, expected_name in data.items():
            slug = Canon(name_or_slug).name
            self.assertEqual(slug, expected_name)

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

class DriverTests(unittest.TestCase):
    def test__best_of_n(self):
        driver = Driver(1942)
        data = {('1', '2', '3'): Decimal('1'),
                ('', '1'): Decimal('1'),
                (' ', '1'): Decimal('1'),
                ('', ' '): None,
                ('1.5+1', '2.5'): Decimal('2.5'),
                ('1.5+2', '1300'): Decimal('5.5')
               }
        for inputs, best in data.items():
            self.assertEqual(best, driver._best_of_n(inputs))
