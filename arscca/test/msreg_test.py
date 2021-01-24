import pdb
from unittest import TestCase

from arscca.models.msreg import Driver, Event
import redis


# Specify database on localhost for testing (with a different db index)
Driver.REDIS = redis.StrictRedis(host='localhost', port=6379, db=8, decode_responses=True)

class TestgDriver(TestCase):
    def setUp(self):
        """
        Clear out redis between tests
        """
        Driver.REDIS.flushdb()

    def valid_driver(self, name, barcode=None):
        """
        Generate a valid driver (minimal fields)
        """
        return Driver({'First Name': name,
                       'Last Name': 'generated',
                       'Member #': barcode,})

    def test_generate_barcode_1(self):
        driver = self.valid_driver('Josh')
        driver.generate_barcode()
        self.assertEqual(driver.stored_barcode, Driver.FIRST_BARCODE)

class TestEvent(TestCase):
    def test_init_1(self):

        msreg = Msreg('arscca/test/msreg/2020-hangover.txt')
        pdb.set_trace()
        self.assertEqual(len(msreg.drivers), 5)

