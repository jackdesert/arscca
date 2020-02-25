import csv
import pdb
import re

class NationalEventDriver:

    YEAR_REGEX = re.compile(r'\d{4}')

    def __init__(self, data):
        self.data = tuple(data)
        self.id = None


    def _keys(self):
        return (
                'primary_rank',
                'secondary_rank',
                'name',
                'car_number',
                'codriver_car_number',
                'car_class',
                'class_rank',
                'car_year',
                'car_model',
                'best_combined',
                'pax_factor',
                'best_combined_pax',
                'run_1',
                'run_2',
                'run_3',
                'run_4',
                'run_5',
                'run_6',
               )

    def as_dict(self):
        output = dict(id=self.id)
        values = list(self.data)

        for key in reversed(self._keys()):
            output[key] = values.pop()

        return output



    @classmethod
    def all(cls, year):
        if not cls.YEAR_REGEX.match(str(year)):
            raise AssertionError

        drivers = []
        filename = f'arscca/static/{year}-national-results.csv'
        try:
            with open(filename, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for index, row in enumerate(reader):
                    driver = cls(row)
                    # driver.id is used as the id of the table row
                    driver.id = index
                    drivers.append(driver)
        except FileNotFoundError:
            print(f'No results found for year {year}')
            return []

        return drivers[1:]



if __name__ == '__main__':
    import sys
    year = sys.argv[1]
    drivers = NationalEventDriver.all(year)
    for driver in drivers:
        print('')
        for key, value in driver.as_dict().items():
            print(f'{key}: {value}')
