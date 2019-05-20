import pdb
import re
from decimal import Decimal
from .pax import Pax
from .photo import Photo

class Driver:
    DNF_REGEX     = re.compile('(dnf)|(dsq)', re.IGNORECASE)
    PENALTY_REGEX = re.compile('\+')
    INF           = 1000

    def __init__(self, year):
        self.year = year

    def pax_factor(self):
        return Pax.factor(self.year, self.car_class)

    def car_class_sortable(self):
        # This is defined as a method only so it can be used to sort a list of drivers
        return self.car_class

    #    def fastest_time(self):
    #        runs = [self.run_1,
    #                self.run_2,
    #                self.run_3,
    #                self.run_4,
    #                self.run_5,
    #                self.run_6]
    #
    #        times = [self.time_from_string(r) for r in runs]
    #        return min(times)
    #
    #    def fastest_pax_time(self):
    #        fastest = self.fastest_time() * self.pax_factor()
    #        if fastest == Decimal('inf'):
    #            return fastest
    #        else:
    #            return fastest.quantize(Decimal('.001'))
    #

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

    def _best_of_three(self, one, two, three):
        runs = [one, two, three]
        runs_to_use = [rr for rr in runs if rr]
        times = [self.time_from_string(rr) for rr in runs_to_use]
        return min(times)

    def best_am(self):
        return self._best_of_three(self.run_1, self.run_2, self.run_3)

    def best_pm(self):
        return self._best_of_three(self.run_4, self.run_5, self.run_6)


    def best_combined(self):
        if self.best_am() and self.best_pm():
            try:
                return self.best_am() + self.best_pm()
            except:
                pdb.set_trace()
        else:
            return self.INF

    def best_combined_pax(self):
        fastest = self.best_combined() * self.pax_factor()
        if fastest == Decimal('inf'):
            return fastest
        else:
            return fastest.quantize(Decimal('.001'))



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
        print(f'best_am       {self.best_am()}')
        print(f'best_pm       {self.best_pm()}')
        print(f'best_combined {self.best_combined()}')
        print(f'best_combined_pax {self.best_combined_pax()}')
        #print(f'fastest_time  {self.fastest_time()}')
        #print(f'fastest_pax   {self.fastest_pax_time()}')

    def properties(self):
        slug_and_head_shot = Photo.slug_and_head_shot(self.name)

        props = self.__dict__.copy()
        props.update(best_combined = str(self.best_combined()),
                     best_combined_pax = str(self.best_combined_pax()),
                     #fastest_time = str(self.fastest_time()),
                     #fastest_pax_time = str(self.fastest_pax_time()),
                     pax_factor = str(self.pax_factor()),
                     slug = slug_and_head_shot.get('slug') or '',
                     headshot = slug_and_head_shot.get('head_shot') or '')
        return props

