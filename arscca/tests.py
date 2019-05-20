import unittest
import pdb

from pyramid import testing
from arscca.models.photo import Photo


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
