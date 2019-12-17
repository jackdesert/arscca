import unittest
import pytest
import pdb


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
