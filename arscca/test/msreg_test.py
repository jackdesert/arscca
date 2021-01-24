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
        """
        Verify that generating a barcode sets it equal to FIRST_BARCODE
        """
        driver = self.valid_driver('Josh')
        driver.generate_barcode()
        self.assertEqual(driver.stored_barcode, Driver.FIRST_BARCODE)

    def test_generate_barcode_2(self):
        """
        Successive calls to generate_barcode() increment
        """
        driver_1 = self.valid_driver('Josh')
        driver_1.generate_barcode()

        driver_2 = self.valid_driver('Allison')
        driver_2.generate_barcode()

        self.assertEqual(int(driver_1.stored_barcode) + 1, int(driver_2.stored_barcode))

class TestEvent(TestCase):
    def test_init_1(self):

        msreg = Msreg('arscca/test/msreg/2020-hangover.txt')
        pdb.set_trace()
        self.assertEqual(len(msreg.drivers), 5)

