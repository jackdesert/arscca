"""
Classes for processing an msreg event export.
Namely, this is used to fill in missing barcodes for non-SCCA-member
and to run sanity checks like no duplicate barcodes and  no duplicate car numbers
"""

import csv
import pdb

from arscca.models.shared import Shared


class Driver:
    """
    A driver registered for an event
    """

    REDIS = Shared.REDIS
    REDIS_KEY = Shared.REDIS_KEY_BARCODES

    # First barcode is easy to pronounce and easy for humans to visually scan
    FIRST_BARCODE = '111200'

    __slots__ = ('message', 'params')

    def __init__(self, params):
        self.params = params
        self.message = None

    @property
    def name(self):
        """
        Concatenate first and last name together

        :return: :str:
        """
        first_name = self.params['First Name']
        last_name = self.params['Last Name']

        return f'{first_name} {last_name}'

    @property
    def barcode(self):
        """
        Find or generate a barcode for this driver using multiple sources

        :return: :str:
        """
        if self.msreg_barcode and self.stored_barcode:
            # Set a message for later
            self.message = f'Barcode changed in Msreg: {self.msreg_barcode}'
            self.remove_stored_barcode()
        return self.msreg_barcode or self.stored_barcode or self.generate_barcode()

    @property
    def msreg_barcode(self):
        """
        The msreg barcode (member number) as downloaded

        :return: :str:
        """
        return self.params['Member #'] or None

    @property
    def stored_barcode(self):
        """
        Retrieve the barcode stored in Redis from a previous msreg export

        :return: :str:
        """
        return self.REDIS.get(f'{self.REDIS_KEY}-{self.name}')

    def generate_barcode(self):
        """
        Generate a unique barcode, store it in redis

        :return: :str:
        """

        values = self.REDIS.hvals(self.REDIS_KEY)
        if values:
            next_barcode = int(max(values)) + 1
        else:
            next_barcode = self.FIRST_BARCODE

        self.REDIS.hset(self.REDIS_KEY, self.name, next_barcode)
        return next_barcode

    def remove_stored_barcode(self):
        """
        Delete barcode from redis
        """
        self.REDIS.hdel(self.REDIS_KEY, self.name)




class Event:
    """
    Class representing an event exported from motorsportreg (msreg)
    """

    __slots__ = ('input_path',)

    def __init__(self, input_path):
        self.input_path = input_path

    @property
    def drivers(self):
        """
        Drivers from event
        """
        output = []
        with open(self.input_path, newline='') as tsv_file:
            reader = csv.DictReader(tsv_file, delimiter='\t')
            pdb.set_trace()
            for line in reader:
                driver = MsregDriver(line)
                output.append(driver)
        output.sort(key=lambda x: x.name)
        return output

    def barcodes(self):
        """
        Barcodes for all drivers
        """
        for driver in self.drivers:
            print(f'{driver.name}: {driver.barcode}')




if __name__ == '__main__':
    msreg = Msreg('arscca/test/msreg/2020-hangover.txt')
    msreg.barcodes()
