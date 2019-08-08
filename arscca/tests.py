import unittest
import pytest
import pdb

from pyramid import testing
from arscca.models.photo import Photo
from arscca.models.gossip import Gossip
from arscca.models.canon import Canon


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from .views import home_view
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

