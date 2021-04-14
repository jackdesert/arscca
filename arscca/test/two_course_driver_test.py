import unittest
import pytest
import pdb

from arscca.models.driver import TwoCourseDriver

from decimal import Decimal
from pyramid import testing
from unittest.mock import patch


class TwoCourseDriverTest(unittest.TestCase):

    @patch('arscca.models.driver.TwoCourseDriver._runs_upper', return_value=('6', '5'))
    def test_best_am__1(self, _runs_upper):
        driver = TwoCourseDriver(None, None, None, None, None)
        self.assertEqual(driver.best_am(), Decimal('5'))

    @patch('arscca.models.driver.TwoCourseDriver._runs_lower', return_value=('40', '50'))
    def test_best_pm__1(self, _runs_lower):
        driver = TwoCourseDriver(None, None, None, None, None)
        self.assertEqual(driver.best_pm(), Decimal('40'))





    # With numerical values
    @patch('arscca.models.driver.TwoCourseDriver._runs_upper', return_value=('25', '22'))
    @patch('arscca.models.driver.TwoCourseDriver._runs_lower', return_value=('40', '50'))
    def test_best_combined_1(self, _runs_lower, _runs_upper):
        driver = TwoCourseDriver(None, None, None, None, None)
        driver.second_half_started = False
        self.assertEqual(driver.best_combined(), Decimal('22'))

        driver.second_half_started = True
        self.assertEqual(driver.best_combined(), Decimal('62'))


    # With no good score in _runs_upper
    @patch('arscca.models.driver.TwoCourseDriver._runs_upper', return_value=('DNF', ' '))
    @patch('arscca.models.driver.TwoCourseDriver._runs_lower', return_value=('25', '22'))
    def test_best_combined_2(self, _runs_lower, _runs_upper):
        driver = TwoCourseDriver(None, None, None, None, None)
        driver.second_half_started = False
        self.assertEqual(driver.best_combined(), TwoCourseDriver.INF)

        driver.second_half_started = True
        self.assertEqual(driver.best_combined(), TwoCourseDriver.INF)

    # With no good score in _runs_lower
    @patch('arscca.models.driver.TwoCourseDriver._runs_upper', return_value=('25', '22'))
    @patch('arscca.models.driver.TwoCourseDriver._runs_lower', return_value=('DNF', ' '))
    def test_best_combined_3(self, _runs_lower, _runs_upper):
        driver = TwoCourseDriver(None, None, None, None, None)
        driver.second_half_started = False
        self.assertEqual(driver.best_combined(), Decimal('22'))

        driver.second_half_started = True
        self.assertEqual(driver.best_combined(), TwoCourseDriver.INF)









    @patch('arscca.models.pax.Pax.factor', return_value=Decimal('0.88888882'))
    @patch('arscca.models.driver.TwoCourseDriver.best_combined', return_value=Decimal('25'))
    def test_best_combined_pax_1(self, factor, best_combined):
        driver = TwoCourseDriver(None, ('0', '1', '2', '3'), tuple(), None, None)
        # Note the result is quantized, which limits decimal places and rounds
        self.assertEqual(driver.best_combined_pax(), Decimal('22.222'))



    # Note this test is different for various subclasses of GenericDriver
    def test_published_primary_score(self):
        driver = TwoCourseDriver(1900, ('3', '4', 'total'), tuple(), None, 2)
        self.assertEqual(driver.published_primary_score, 'total')





    # With second_half_started = True
    @patch('arscca.models.driver.TwoCourseDriver.best_combined', return_value=Decimal('35'))
    def test_error_in_published_1(self, best_combined):
        driver = TwoCourseDriver(None, ('', '', '', 'Rodrigo', '', '', '36'), tuple(), None, 6)
        driver.second_half_started = True
        error = driver.error_in_published()
        expected = {'driver_name': 'Rodrigo', 'calculated': 35.0, 'published': 36.0}
        self.assertEqual(error, expected)

    # With second_half_started = False (published will be DNS)
    @patch('arscca.models.driver.TwoCourseDriver.best_combined', return_value=Decimal('35'))
    def test_error_in_published_2(self, best_combined):
        driver = TwoCourseDriver(None, ('', '', '', 'Rodrigo', '', '', 'DNS'), tuple(), None, 6)
        driver.second_half_started = False
        error = driver.error_in_published()
        self.assertEqual(error, None)







    @patch('arscca.models.photo.Photo.slug_and_head_shot', return_value=dict(photo='p', head_shot='h'))
    @patch('arscca.models.pax.Pax.factor', return_value=Decimal('0.95'))
    @patch('arscca.models.driver.TwoCourseDriver.best_combined', return_value=Decimal('37'))
    def test_properties(self, slug_and_head_shot, factor, primary_score):
        driver = TwoCourseDriver(2017,
            ('0', 'ss', '2', 'Rodrigo', '4', '5', '6',  '7',  '8', '9+1', '100'),
            (' ', ' ',  ' ', ' ',       ' ', ' ', ' ', '10', '11', '12',   'anything'),
            7,
            10)
        driver.second_half_started = True

        expected = {'year': 2017, 'name': 'Rodrigo', 'car_class': 'ss', 'car_model': '4', 'car_number': '2', 'id': 'rodrigo--ss_2', 'second_half_started': True, 'runs_upper_best_index': 0, 'runs_upper': ('7', '8', '9+1'), 'runs_lower_best_index': 0, 'runs_lower': ('10', '11', '12'), 'published_primary_score': '100', 'primary_score': '37', 'secondary_score': '35.150', 'pax_factor': '0.95', 'slug': '', 'headshot': 'h'}

        self.assertEqual(driver.properties(), expected)




