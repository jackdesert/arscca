import unittest
import pytest
import pdb


from pyramid import testing
from unittest.mock import patch


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



class LogSplitterTest(unittest.TestCase):

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
