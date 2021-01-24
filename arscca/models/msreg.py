"""
Classes for processing an msreg event export.
Namely, this is used to:

    - Generate blank and invalid barcodes with generated barcodes
    - Verify no duplicate barcodes
    - Verify no duplicate car classes

"""

from copy import copy
import csv
import pdb


from arscca.models.shared import Shared


class Driver:
    """
    A driver registered for an event
    """
    COMMA_AND_SPACE = ', '

    REDIS = Shared.REDIS
    REDIS_KEY = Shared.REDIS_KEY_BARCODES

    BARCODE_COLUMN = 'Member #'
    MESSAGES_COLUMN = 'Messages'

    # First barcode is easy to pronounce and easy for humans to visually scan
    FIRST_BARCODE = '111200'

    __slots__ = ('messages', 'params')

    def __init__(self, params):
        self.params = params
        self.messages = set()

    def as_dict(self):
        output = copy(self.params)
        output[self.BARCODE_COLUMN] = self.barcode
        output[self.MESSAGES_COLUMN] = self.COMMA_AND_SPACE.join(self.messages) or None
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
            self.messages.add(f'Barcode changed in Msreg to "{self.msreg_barcode}"')
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
        if not value:
            return None

        value = str(value).strip()
        if len(value) == 6:
            return value

        # Strings shorter or longer than 6 characters
        self.messages.add(f'msreg gave barcode "{value}" so generating new')
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

    __slots__ = ('_input_path', '_fieldnames', '_drivers')

    def __init__(self, input_path):
        self._input_path = input_path
        self._fieldnames = None
        self._drivers = None

    @property
    def drivers(self):
        if self._drivers is None:
            self._drivers = self._fetch_drivers()
        return self._drivers

    def _fetch_drivers(self):
        """
        Drivers from event
        """
        output = []
        with open(self._input_path, newline='') as tsv_file:
            reader = csv.DictReader(tsv_file, delimiter=self.TAB)
            self._fieldnames = reader.fieldnames
            for line in reader:
                driver = Driver(line)
                output.append(driver)
        output.sort(key=lambda x: x.name)
        return output


    def write_to_file(self, location='/tmp/msreg_augmented.txt'):
        fieldnames_to_use = copy(self._fieldnames)
        fieldnames_to_use.append(Driver.MESSAGES_COLUMN)

        with open(location, 'w', newline='') as tsv_file:
            writer = csv.DictWriter(
                tsv_file, fieldnames=fieldnames_to_use, delimiter=self.TAB
            )
            writer.writeheader()
            for driver in self.drivers:
                writer.writerow(driver.as_dict())

    def notify_if_duplicate_barcodes(self):
        """
        Add a message to each driver with a duplicate barcode.
        Returns the total number of affected drivers.
        For example, if two drivers have the same barcode,
        this method will return the integer 2.

        :return: :int:
        """
        count = 0
        barcodes = tuple([driver.barcode for driver in self.drivers])
        for driver in self.drivers:
            if barcodes.count(driver.barcode) > 1:
                driver.messages.add('Duplicate barcode')
                count += 1
        return count



if __name__ == '__main__':

    # Use local redis for inspection
    import redis

    Driver.REDIS = redis.StrictRedis(
        host='localhost', port=6379, db=9, decode_responses=True
    )

    msreg = Event('arscca/test/msreg/2020-hangover.txt')
    msreg.write_to_file('/tmp/msreg.txt')
