import unittest
import pytest
import pdb

from arscca.models.driver import Driver
from arscca.models.driver import TwoCourseDriver

from decimal import Decimal
from pyramid import testing
from unittest.mock import patch


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
    def test__penalty_from_pylons(self):
        data = {'1': 2,
                '2': 4}
        driver = Driver(1942)
        for pylon_count, penalty_in_seconds in data.items():
            self.assertEqual(driver._penalty_from_pylons(pylon_count), penalty_in_seconds)

    def test_time_from_string(self):
        data = {'36': Decimal('36'),
                '42.334+2': Decimal('46.334'),
                '40+2/1': Decimal('54.000'), # One missed gate
                '40+1/0': Decimal('42.000'), # Zero missed gates
                '90+': Decimal('90'),
                '90+ ': Decimal('90'),
                '30+dnf': Driver.INF,
                '30+dns': Driver.INF}
        driver = Driver(1942)

        for string, time in data.items():
            self.assertEqual(driver.time_from_string(string), time)

    def test_best_am(self):
        driver = TwoCourseDriver(1942)
        driver.runs_upper = ['10.2', '11', '9.335']
        driver.runs_lower = ['1.2', '11', '9.335']
        self.assertEqual(driver.best_am(), Decimal('9.335'))

    def test_best_pm(self):
        driver = TwoCourseDriver(1942)
        driver.runs_upper = ['2.5', '8.611', '9.335']
        driver.runs_lower = ['10.2', '8.611', '9.335']
        self.assertEqual(driver.best_pm(), Decimal('8.611'))

    def test_runs_upper_only(self):
        driver = TwoCourseDriver(1942)
        driver.second_half_started = False
        self.assertEqual(driver.runs_upper_only, True)

        driver.second_half_started = True
        self.assertEqual(driver.runs_upper_only, False)

    def test_best_combined_1(self):
        driver = TwoCourseDriver(1942)
        driver.second_half_started = False
        driver.runs_upper = ['10', '12', '9']
        driver.runs_lower = []
        self.assertEqual(driver.best_combined(), Decimal('9'))

    def test_best_combined_2(self):
        driver = TwoCourseDriver(1942)
        driver.second_half_started = True
        driver.runs_upper = ['10', '12', '9']
        driver.runs_lower = ['21', '22', '18+1']
        self.assertEqual(driver.best_combined(), Decimal('29'))

    def test_best_combined_3(self):
        driver = TwoCourseDriver(1942)
        driver.second_half_started = False
        driver.runs_upper = []
        driver.runs_lower = []
        self.assertEqual(driver.best_combined(), Driver.INF)

    def test_best_combined_4(self):
        driver = TwoCourseDriver(1942)
        driver.second_half_started = True
        driver.runs_upper = []
        driver.runs_lower = ['21', '22', '18+1']
        self.assertEqual(driver.best_combined(), Driver.INF)

    def test_best_combined_5(self):
        driver = TwoCourseDriver(1942)
        driver.second_half_started = True
        driver.runs_upper = ['21', '22', '18+1']
        driver.runs_lower = []
        self.assertEqual(driver.best_combined(), Driver.INF)

    def test_error_in_published(self):
        driver = TwoCourseDriver(1942)
        driver.name = 'Rodrigo'
        driver.second_half_started = True
        driver.runs_upper = ['21', '22', '18+1']
        driver.runs_lower = ['28']
        driver.published_primary_score = '100'
        error = driver.error_in_published()
        expected = {'driver_name': 'Rodrigo', 'calculated': 48.0, 'published': 100.0}
        self.assertEqual(error, expected)

    @patch('arscca.models.photo.Photo.slug_and_head_shot', return_value=dict(photo='p', head_shot='h'))
    @patch('arscca.models.pax.Pax.factor', return_value=Decimal('0.95'))
    def test_properties(self, slug_and_head_shot, factor):
        driver = TwoCourseDriver(1942)
        driver.name = 'Rodrigo'
        driver.car_class = 'anything'
        driver.second_half_started = True
        driver.runs_upper = ['21', '22', '18+1']
        driver.runs_lower = ['28']
        driver.published_primary_score = '100'

        expected = {'year': 1942, 'name': 'Rodrigo', 'car_class': 'anything', 'second_half_started': True, 'runs_upper': ['21', '22', '18+1'], 'runs_lower': ['28'], 'published_primary_score': '100', 'primary_score': '48', 'secondary_score': '45.600', 'pax_factor': '0.95', 'slug': '', 'headshot': 'h'}

        self.assertEqual(driver.properties(), expected)




    @patch('arscca.models.pax.Pax.factor', return_value=Decimal('0.88888882'))
    def test_best_combined_pax_1(self, factor):
        driver = TwoCourseDriver(1942)
        driver.car_class = 'anything'
        driver.second_half_started = False
        driver.runs_upper = ['21', '22', '']
        driver.runs_lower = []
        # Note the result is quantized, which limits decimal places and rounds
        self.assertEqual(driver.best_combined_pax(), Decimal('18.667'))

    @patch('arscca.models.pax.Pax.factor', return_value=Decimal('0.8'))
    def test_best_combined_pax_2(self, factor):
        driver = TwoCourseDriver(1942)
        driver.car_class = 'anything'
        driver.second_half_started = True
        driver.runs_upper = ['21', '22', '']
        driver.runs_lower = []
        self.assertEqual(driver.best_combined_pax(), Driver.INF)

