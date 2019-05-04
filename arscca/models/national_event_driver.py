import csv
import pdb

class NationalEventDriver:

    def __init__(self, data):
        self.data = tuple(data)
        self.id = None


    def _keys(self):
        return (
                'position_overall',
                'position_pax',
                'name',
                'car_number',
                'codriver_car_number',
                'car_class',
                'position_class',
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
    def all(cls):
        drivers = []
        with open('arscca/static/2018-national-results.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for index, row in enumerate(reader):
                driver = cls(row)
                # driver.id is used as the id of the table row
                driver.id = index
                drivers.append(driver)
        return drivers[1:]



if __name__ == '__main__':
    drivers = NationalEventDriver.all()
    for driver in drivers:
        print('')
        for key, value in driver.as_dict().items():
            print(f'{key}: {value}')
