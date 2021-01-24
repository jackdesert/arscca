"""
Classes for processing an msreg event export.
Namely, this is used to fill in missing barcodes for non-SCCA-member
and to run sanity checks like no duplicate barcodes and  no duplicate car numbers
"""

from copy import copy
import csv
import pdb


from arscca.models.shared import Shared


class Driver:
    """
    A driver registered for an event
    """

    REDIS = Shared.REDIS
    REDIS_KEY = Shared.REDIS_KEY_BARCODES

    BARCODE_COLUMN = 'Member #'

    # First barcode is easy to pronounce and easy for humans to visually scan
    FIRST_BARCODE = '111200'

    __slots__ = ('message', 'params')

    def __init__(self, params):
        self.params = params
        self.message = None

    def as_dict(self):
        output = copy(self.params)
        output[self.BARCODE_COLUMN] = self.barcode
        return output

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
        The msreg barcode (member number) as downloaded.

        Returns None if the barcode is shorter or longer than 6 characters after stripping.
        That way any garbage values will be replaced by a barcode that we generate.


        :return: :str: or :None:
        """
        value = self.params[self.BARCODE_COLUMN]
        if not isinstance(value, str):
            # Non-strings return here
            return None

        value = value.strip()
        if len(value) == 6:
            return value

        # Strings shorter or longer than 6 characters
        return None


    @property
    def stored_barcode(self):
        """
        Retrieve the barcode stored in Redis from a previous msreg export

        :return: :str:
        """
        return self.REDIS.hget(self.REDIS_KEY, self.name)

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

    TAB = '\t'

    __slots__ = ('input_path', 'fieldnames')

    def __init__(self, input_path):
        self.input_path = input_path
        self.fieldnames = None

    @property
    def drivers(self):
        """
        Drivers from event
        """
        output = []
        with open(self.input_path, newline='') as tsv_file:
            reader = csv.DictReader(tsv_file, delimiter=self.TAB)
            self.fieldnames = reader.fieldnames
            for line in reader:
                driver = Driver(line)
                output.append(driver)
        output.sort(key=lambda x: x.name)
        return output

    def barcodes(self):
        """
        Barcodes for all drivers
        """
        for driver in self.drivers:
            print(f'{driver.name}: {driver.barcode}')

    def write_to_file(self, location='/tmp/msreg_augmented.txt'):
        with open(location, 'w', newline='') as tsv_file:
            writer = csv.DictWriter(tsv_file, fieldnames=self.fieldnames, delimiter=self.TAB)
            writer.writeheader()
            for driver in self.drivers:
                writer.writerow(driver.as_dict())




if __name__ == '__main__':

    # Use local redis for inspection
    import redis
    Driver.REDIS = redis.StrictRedis(host='localhost', port=6379, db=9, decode_responses=True)

    msreg = Event('arscca/test/msreg/2020-hangover.txt')
    print(msreg.barcodes())
    msreg.write_to_file()
