import pdb
from unittest import TestCase
from unittest.mock import patch, MagicMock, PropertyMock

from arscca.models.msreg import Driver, Event
import redis


# Specify database on localhost for testing (with a different db index)
Driver.REDIS = redis.StrictRedis(host='localhost', port=6379, db=8, decode_responses=True)


def valid_driver(name, barcode=None, car_class='STS', number='77'):
    """
    Generate a valid driver (minimal fields)
    """
    return Driver({'First Name': name,
                   'Last Name': 'generated',
                   'Member #': barcode,
                   'Class': car_class,
                   'Number': number,
                   })

class TestDriver(TestCase):
    def setUp(self):
        """
        Clear out redis between tests
        """
        Driver.REDIS.flushdb()


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
            driver = valid_driver('Josh', b_in)
            self.assertEqual(driver.msreg_barcode, b_out)



    def test_generate_barcode_1(self):
        """
        Verify that generating a barcode sets it equal to FIRST_BARCODE
        """
        driver = valid_driver('Josh')
        driver.generate_barcode()
        self.assertEqual(driver.stored_barcode, Driver.FIRST_BARCODE)

    def test_generate_barcode_2(self):
        """
        Successive calls to generate_barcode() increment
        """
        driver_1 = valid_driver('Josh')
        driver_1.generate_barcode()

        driver_2 = valid_driver('Allison')
        driver_2.generate_barcode()

        self.assertEqual(int(driver_1.stored_barcode) + 1, int(driver_2.stored_barcode))

    def test_remove_stored_barcode(self):
        """
        Verify that barcode is removed from redis
        """
        driver = valid_driver('Josh')
        driver.generate_barcode()

        assert isinstance(driver.stored_barcode, str)
        driver.remove_stored_barcode()
        assert(driver.stored_barcode is None)

    def test_barcode_1(self):
        """
        When barcode in msreg, verify that barcode is used
        """
        driver = valid_driver('Josh', '000000')
        self.assertEqual(driver.barcode, '000000')

    @patch('arscca.models.msreg.Driver.stored_barcode', PropertyMock(return_value='333333'))
    def test_barcode_2(self):
        """
        When no barcode in msreg, and there is a stored barcode, use the stored barcode
        """
        driver = valid_driver('Elizabeth')
        self.assertEqual(driver.barcode, '333333')

    @patch('arscca.models.msreg.Driver.generate_barcode', MagicMock(return_value='222222'))
    def test_barcode_3(self):
        """
        When no barcode in msreg and no stored_barcode, generate a barcode
        """
        driver = valid_driver('Elizabeth')
        self.assertEqual(driver.barcode, '222222')


class TestEvent(TestCase):
    def test_init_1(self):

        msreg = Event('arscca/test/msreg/2020-hangover.txt')
        self.assertEqual(len(msreg.drivers), 45)

    def test_notify_if_duplicate_barcodes_1(self):
        barcode = '111222'
        fred = valid_driver('Fred', barcode)
        allison = valid_driver('Allison', barcode)
        melanie = valid_driver('Melanie', '333444')
        event = Event(None)
        event._drivers = [fred, allison, melanie]
        count = event._notify_if_duplicate_barcodes()

        self.assertEqual(2, count)
        self.assertEqual(fred.messages, {'Duplicate barcode'})
        self.assertEqual(allison.messages, {'Duplicate barcode'})
        self.assertEqual(melanie.messages, set())

    def test_notify_if_duplicate_car_class_and_number_1(self):
        fred = valid_driver('Fred', car_class='SM', number='5')
        allison = valid_driver('Allison', car_class='DS', number='5')
        melanie = valid_driver('Melanie', car_class='DS', number='5')

        event = Event(None)
        event._drivers = [fred, allison, melanie]
        count = event._notify_if_duplicate_car_class_and_number()

        self.assertEqual(2, count)
        self.assertEqual(fred.messages, set())
        self.assertEqual(allison.messages, {'Duplicate car class & number'})
        self.assertEqual(melanie.messages, {'Duplicate car class & number'})

