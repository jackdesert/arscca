"""
Classes for processing an msreg event export.
Namely, this is used to:

    - Generate blank and invalid barcodes with generated barcodes
    - Verify no duplicate barcodes
    - Verify no duplicate car classes

"""

from collections import defaultdict
from copy import copy
from datetime import datetime
import csv
import os
import pdb


from arscca.models.pax import Pax
from arscca.models.shared import Shared


class Driver:
    """
    A driver registered for an event
    """

    COMMA_AND_SPACE = ', '

    REDIS = Shared.REDIS
    REDIS_KEY = Shared.REDIS_KEY_BARCODES

    CAR_CLASS_COLUMN = 'Class'
    CAR_MODEL_COLUMN = 'Car Model'
    NUMBER_COLUMN = 'Number'
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
    def car_class_and_number(self):
        number = self.params[self.NUMBER_COLUMN]
        return f'{self.car_class} {number}'

    @property
    def car_class(self):
        return self.params[self.CAR_CLASS_COLUMN]

    @property
    def car_model(self):
        return self.params[self.CAR_MODEL_COLUMN]

    @property
    def barcode(self):
        """
        Find or generate a barcode for this driver using multiple sources

        :return: :str:
        """

        if self.msreg_barcode and self.stored_barcode:
            # Set a message for later
            self.messages.add(
                f'Print a new barcode for {self.name} because barcode updated in msreg to "{self.msreg_barcode}"'
            )
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
        self.messages.add(f'Generated new because msreg gave barcode "{value}"')
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
    SECONDS_PER_MINUTE = 60

    __slots__ = ('_input_path', '_fieldnames', '_drivers')

    def __init__(self, input_path=Shared.MSREG_RAW_PATH):
        self._input_path = input_path
        self._fieldnames = None
        self._drivers = None

    @property
    def drivers(self):
        if self._drivers is None:
            self._drivers = self._fetch_drivers_and_verify()
            self._notify_if_duplicate_barcodes()
            self._notify_if_no_pax_entry_for_class()
            self._notify_if_duplicate_car_class_and_number()

        return self._drivers

    @property
    def minutes_ago(self):
        unix_tstamp = os.path.getmtime(Shared.MSREG_RAW_PATH)
        tstamp = datetime.fromtimestamp(unix_tstamp)
        delta_seconds = (datetime.now() - tstamp).total_seconds()
        delta_minutes = delta_seconds / self.SECONDS_PER_MINUTE
        return round(delta_minutes, 1)

    def _fetch_drivers_and_verify(self):
        """
        Drivers from event
        """
        output = []
        with open(self._input_path, newline='') as tsv_file:
            reader = csv.DictReader(tsv_file, delimiter=self.TAB)
            # Simple check to make sure this is a TSV file
            if len(reader.fieldnames) < 2:
                return []
            self._fieldnames = reader.fieldnames
            for line in reader:
                driver = Driver(line)
                output.append(driver)
        output.sort(key=lambda x: x.name)
        return output

    def write_to_file(self):
        fieldnames_to_use = copy(self._fieldnames)
        fieldnames_to_use.append(Driver.MESSAGES_COLUMN)

        with open(Shared.MSREG_AUGMENTED_PATH, 'w', newline='') as tsv_file:
            writer = csv.DictWriter(
                tsv_file, fieldnames=fieldnames_to_use, delimiter=self.TAB
            )
            writer.writeheader()

            for driver in self.drivers:
                writer.writerow(driver.as_dict())

    def _notify_if_duplicate_barcodes(self):
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

    def _notify_if_duplicate_car_class_and_number(self):
        """
        Add a message to each driver with a duplicate car class & number.
        Returns the total number of affected drivers.
        For example, if two drivers are both registered as CAMT 25,
        this method will return the integer 2.

        :return: :int:
        """

        class_map = defaultdict(list)

        for driver in self.drivers:
            class_map[driver.car_class_and_number].append(driver.name)

        count = 0
        for driver in self.drivers:
            if len(class_map[driver.car_class_and_number]) > 1:
                driver.messages.add('Duplicate car class & number')
                count += 1
        return count

    def _notify_if_no_pax_entry_for_class(self):
        """
        Adds a message to each driver with a class not listed in arscca.models.pax.Pax
        """
        year = datetime.now().year
        for driver in self.drivers:
            try:
                # pylint: disable=unused_variable
                unused_pax_factor = Pax.factor(year, driver.car_class)
            except KeyError:
                driver.messages.add(f'Unknown car class: {driver.car_class}')


if __name__ == '__main__':

    # Use local redis for inspection
    import redis

    Driver.REDIS = redis.StrictRedis(
        host='localhost', port=6379, db=9, decode_responses=True
    )

    # msreg = Event('arscca/test/msreg/2020-hangover.txt')
    msreg = Event('arscca/test/msreg/2020-hangover-with-dupes.txt')
    msreg.write_to_file()
