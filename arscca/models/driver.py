import pdb
import re
from decimal import Decimal
from .pax import Pax

class Driver:
    DNF_REGEX     = re.compile('dnf', re.IGNORECASE)
    PENALTY_REGEX = re.compile('\+')

    def __init__(self):
        pass

    def pax_factor(self):
        return Pax.factor(self.car_class)

    def car_class_sortable(self):
        # This is defined as a method only so it can be used to sort a list of drivers
        return self.car_class

    def fastest_time(self):
        runs = [self.run_1,
                self.run_2,
                self.run_3,
                self.run_4,
                self.run_5,
                self.run_6]

        times = [self.time_from_string(r) for r in runs]
        return min(times)

    def fastest_pax_time(self):
        fastest = self.fastest_time() * self.pax_factor()
        if fastest == Decimal('inf'):
            return fastest
        else:
            return fastest.quantize(Decimal('.001'))

    def time_from_string(self, string):
        if self.DNF_REGEX.search(string) or (string == '\xa0'):
            return Decimal('inf')
        if self.PENALTY_REGEX.search(string):
            time, delay = string.split('+')
            time = Decimal(time)
            delay = int(delay)
        else:
            time = Decimal(string)
            delay = 0

        return time + delay

    def print(self):
        print('')
        print(f'name          {self.name}')
        print(f'car_number    {self.car_number}')
        print(f'car_class     {self.car_class}')
        print(f'car_model     {self.car_model}')
        print(f'run_1         {self.run_1}')
        print(f'run_2         {self.run_2}')
        print(f'run_3         {self.run_3}')
        print(f'run_4         {self.run_4}')
        print(f'run_5         {self.run_5}')
        print(f'run_6         {self.run_6}')
        print(f'fastest_time  {self.fastest_time()}')
        print(f'fastest_pax   {self.fastest_pax_time()}')


