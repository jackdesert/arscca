import itertools
import unittest
import pytest
import pdb

from arscca.models.canon import Canon
from arscca.models.driver import Driver
from arscca.models.driver import TwoCourseDriver
from arscca.models.gossip import Gossip
from arscca.models.histogram import Histogram
from arscca.models.live_event_presenter import LiveEventPresenter
from arscca.models.parser import StandardParser
from arscca.models.parser import BestTimeParser
from arscca.models.pax import Pax
from arscca.models.photo import Photo
from arscca.models.short_queue import ShortQueue
from arscca.models.util import Util

from decimal import Decimal
from pyramid import testing
from unittest.mock import patch


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
        data = Photo.slug_and_head_shot('Adam. Cadorette')
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
    def test_random_run_groups(self):
        data = {'as': ['George', 'Carla'],
                'bs': ['Amy'],
                'bsl': ['Claudia'],
                'cs': ['Barney', 'Samantha'],
                'ds': ['Jesus', 'Cepia', 'Pink'],
                'es': ['Frank', 'Elizabeth', 'Becki', 'Roosevelt'],
                'fs': ['Michele', 'Tara', 'Vicki'],
                'gs': ['Joan', 'Mia'],
                'jm': ['Fred']}
        # Run this multiple times, since the results are stochastic for large samples
        for i in range(7):
            groups, counter = Util.randomize_run_groups(data)
            for group in groups[0:2]:
                if 'bs' in group:
                    assert 'bsl' in group
            drivers_0 = list(itertools.chain(*groups[0].values()))
            drivers_1 = list(itertools.chain(*groups[1].values()))
            assert counter[0] == len(drivers_0)
            assert counter[1] == len(drivers_1)
            assert abs(len(drivers_0) - len(drivers_1)) < 3
            assert groups[2] == {'jm': ['Fred']}

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


class ShortQueueTests(unittest.TestCase):
    # Note these tests do not actually exercise the locking mechanisms in the class
    def test__join(self):
        queue = ShortQueue()
        self.assertEqual(queue.join(), True)
        self.assertEqual(queue.join(), False)
        self.assertEqual(queue.join(), False)
        self.assertEqual(queue.join(), False)

    def test__join_then_leave_then_join(self):
        queue = ShortQueue()
        self.assertEqual(queue.join(), True)
        queue.leave()
        self.assertEqual(queue.join(), True)

    def test__leave(self):
        queue = ShortQueue()
        with pytest.raises(ValueError):
            self.assertEqual(queue.leave(), True)

class HistogramTests(unittest.TestCase):
    # Note these tests do not actually exercise the locking mechanisms in the class
    def test__conformed_values(self):
        values = [10, 11, 15, 20, 22, 25]
        conformed_values, num_conformed = Histogram._conformed_values(values)
        expected = [10.0, 11.0, 15.0, 20.0, 20.0, 20.0]
        self.assertEqual(conformed_values, expected)
        self.assertEqual(num_conformed, 2)

    def test__bin_specification(self):
        min_value = 98
        max_value = 167
        num_values = 16
        width, quantity = Histogram._bin_specification(min_value, max_value, num_values)
        self.assertEqual(width, 10)
        self.assertEqual(quantity, 5)


    def test__bins_1(self):
        values = [99, 102, 112, 113, 110, 99, 101, 102, 102, 102, 102, 110]

        # Using a default bin width
        bins = Histogram._bins(values, 2)
        self.assertEqual(bins.tolist(), [98, 100, 102, 104, 106, 108, 110, 112, 114])

    def test__bins_2(self):
        values = [98, 102, 112, 114, 110, 99, 101, 102, 102, 102, 102, 110]

        # Using a default bin width
        bins = Histogram._bins(values, 2)
        self.assertEqual(bins.tolist(), [98, 100, 102, 104, 106, 108, 110, 112, 114, 116])


    @patch('arscca.models.histogram.Histogram._bin_specification', return_value=(4, 0))
    def test__bins_3(self, bin_spec):
        values = [98, 102, 112, 114, 110, 99, 101, 102, 102, 102, 102, 110]

        # Using a dynamic bin width, specified in the patch above
        bins = Histogram._bins(values, 0)
        self.assertEqual(bins.tolist(), [96, 100, 104, 108, 112, 116])



# Helper Method
def csv_to_list(string):
    # To generate "csv",
    # - copy table data
    # - paste into gnumeric
    # - export to csv
    # - copy CSV
    # remove blank rows
    # Remove double quotes around fields
    output = [row.split(',') for row in string.split('\n')]
    return output



class StandardParserTests(unittest.TestCase):

    def test__parse_drivers_1(self):
        csv = '''1T,ss,1,Aaron Houff,2007 Porsche,Black,D1,37.856+1,38.058,44.718+1,,,,,,,,74.975
,,,,,,D2,36.917,36.987,37.153,,,,,,,,'''
        data = csv_to_list(csv)
        parser = StandardParser('2018-01-01', '', False)
        drivers = parser._parse_drivers(data)
        self.assertEqual(len(drivers), 1, 'Only one driver')
        driver = drivers[0]
        self.assertEqual(driver.name, 'Aaron Houff')
        self.assertEqual(driver.car_class, 'ss')
        self.assertEqual(driver.car_number, '1')
        self.assertEqual(driver.car_model, '2007 Porsche')
        self.assertEqual(driver.runs_upper, ['37.856+1','38.058','44.718+1'])
        self.assertEqual(driver.runs_lower, ['36.917','36.987','37.153'])
        self.assertEqual(driver.published_primary_score, '74.975')

    def test__parse_drivers_2(self):
        csv = '''1T,ss,1,"Aaron Houff","2007 Porche 911",,D1,37.094+dnf,35.173,34.265,68.957
,,,,,,D2,37.808+dnf,36.029+dnf,34.692,[-]2.384
2,ss,6,"John Buczynski","2018 Alfa Romeo 4C",White,D1,38.166,35.968,35.555+1,71.341
,,,,,,D2,35.879,35.528,35.373,2.384'''
        data = csv_to_list(csv)
        parser = StandardParser('2018-01-01', '', False)
        drivers = parser._parse_drivers(data)
        self.assertEqual(len(drivers), 2, 'Two drivers')



class BestTimeParserTests(unittest.TestCase):


    def test__parse_drivers_1(self):
        csv = '''1T,cs,180,David Lousteau,1965 AC Shelby Cobra,Black,71.926,70.482,69.554,72.31,71.708,71.192,69.554,[-]1.256'''
        data = csv_to_list(csv)
        parser = BestTimeParser('2018-01-01', '', False)
        drivers = parser._parse_drivers(data)
        self.assertEqual(len(drivers), 1, 'Only one driver')
        driver = drivers[0]
        self.assertEqual(driver.name, 'David Lousteau')
        self.assertEqual(driver.car_class, 'cs')
        self.assertEqual(driver.car_number, '180')
        self.assertEqual(driver.car_model, '1965 AC Shelby Cobra')
        self.assertEqual(driver.runs_upper, ['71.926','70.482','69.554', '72.31','71.708','71.192'])
        self.assertEqual(driver.runs_lower, [])
        self.assertEqual(driver.published_primary_score, '69.554')

    def test__parse_drivers_2(self):
        csv = '''1T,cs,180,"David Lousteau","1965 AC Shelby Cobra",Black,71.926,70.482,69.554,72.31,71.708,71.192,69.554,[-]1.256
2,cs,80,"Michael Ford","2017 Mazda MX-5",Black,70.81,78.044,77.124,73.004,72.508,73.592,70.81,1.256
1T,ds,76,"Nicholas Mellenthin","Subaru Wrx",White,68.76,67.965,67.617+1,69.994,70.539,,67.965,[-]0.852
2,ds,176,"shawn mcallister","2013 Subaru WRX",WHITE,70.467,68.763+dnf,68.817,71.76,73.578,,68.817,0.852'''
        data = csv_to_list(csv)
        parser = BestTimeParser('2018-01-01', '', False)
        drivers = parser._parse_drivers(data)
        self.assertEqual(len(drivers), 4, 'Four drivers')
