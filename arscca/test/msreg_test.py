import pdb
from unittest import TestCase
from unittest.mock import patch, MagicMock, PropertyMock

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

    def test_msreg_barcode_1(self):
        """
        Return 6-character barcode verbatim
        """
        barcodes = {
                # Normal
                '123456': '123456',
                # Strips spaces
                ' 123456 ': '123456',
                # Returns None for any that are the wrong length
                '1234567': None,
                '12345': None,
                }
        for b_in, b_out in barcodes.items():
            driver = self.valid_driver('Josh', b_in)
            self.assertEqual(driver.msreg_barcode, b_out)



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

    def test_remove_stored_barcode(self):
        """
        Verify that barcode is removed from redis
        """
        driver = self.valid_driver('Josh')
        driver.generate_barcode()

        assert isinstance(driver.stored_barcode, str)
        driver.remove_stored_barcode()
        assert(driver.stored_barcode is None)

    def test_barcode_1(self):
        """
        When barcode in msreg, verify that barcode is used
        """
        driver = self.valid_driver('Josh', '000000')
        self.assertEqual(driver.barcode, '000000')

    @patch('arscca.models.msreg.Driver.stored_barcode', PropertyMock(return_value='333333'))
    def test_barcode_2(self):
        """
        When no barcode in msreg, and there is a stored barcode, use the stored barcode
        """
        driver = self.valid_driver('Elizabeth')
        self.assertEqual(driver.barcode, '333333')

    @patch('arscca.models.msreg.Driver.generate_barcode', MagicMock(return_value='222222'))
    def test_barcode_3(self):
        """
        When no barcode in msreg and no stored_barcode, generate a barcode
        """
        driver = self.valid_driver('Elizabeth')
        self.assertEqual(driver.barcode, '222222')


class TestEvent(TestCase):
    def test_init_1(self):

        msreg = Event('arscca/test/msreg/2020-hangover.txt')
        self.assertEqual(len(msreg.drivers), 45)

