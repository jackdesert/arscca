import pdb
import re
from decimal import Decimal
from decimal import InvalidOperation
from .pax import Pax
from .photo import Photo

class Driver:
    DNF_REGEX     = re.compile('(dnf)|(dns)|(dsq)', re.IGNORECASE)
    TIME_AND_PENALTY_REGEX = re.compile('([0-9.]+)(\+(\d)(/(\d))?)?')
    INF           = Decimal('inf')

    PYLON_PENALTY_IN_SECONDS = 2
    MISSED_GATE_PENALTY_IN_SECONDS = 10

    def __init__(self, year):
        self.year = year
        # See Parser.parse() for a list of instance variables stored on Driver

    def pax_factor(self):
        return Pax.factor(self.year, self.car_class)

    def car_class_sortable(self):
        # This is defined as a method only so it can be used to sort a list of drivers
        return self.car_class

    def _penalty_from_pylons(self, num_pylons):
        # Sometimes the official results have something like '25.625+ '
        # We count no penalty in this instance
        if num_pylons:
            return int(num_pylons) * self.PYLON_PENALTY_IN_SECONDS
        return 0

    def _penalty_from_gates(self, num_gates):
        if num_gates:
            return int(num_gates) * self.MISSED_GATE_PENALTY_IN_SECONDS
        return 0

    def time_from_string(self, string):
        if self.DNF_REGEX.search(string) or (string == '\xa0'):
            return self.INF

        search = self.TIME_AND_PENALTY_REGEX.search(string)
        if search:
            time = Decimal(search[1])
            num_pylons = search[3] # Will be None or str
            num_gates = search[5]  # Will be None or str

            pylon_penalty = self._penalty_from_pylons(num_pylons)
            gate_penalty  = self._penalty_from_gates(num_gates)
        else:
            # WHY ARE WE HERE?
            pdb.set_trace()
            1
            #time = Decimal(string)
            #penalty = 0

        return time + pylon_penalty + gate_penalty

    def _best_of_n(self, runs):
        runs_to_use = [rr for rr in runs if rr.strip()]
        times = [self.time_from_string(rr) for rr in runs_to_use]
        if times:
            return min(times)

    def best_am(self):
        return self._best_of_n(self.runs_upper)

    def best_pm(self):
        return self._best_of_n(self.runs_lower)

    def runs(self):
        return self.runs_upper + self.runs_lower

    def best_run(self):
        runs = self.runs()
        return self._best_of_n(runs) or self.INF

    def best_run_pax(self):
        best = self.best_run() * self.pax_factor()
        if best == self.INF:
            return best
        else:
            return best.quantize(Decimal('.001'))

    @property
    def runs_upper_only(self):
        return not self.second_half_started

    def best_combined(self):
        if self.best_am() and self.best_pm():
            return self.best_am() + self.best_pm()
        elif self.best_am() and self.runs_upper_only:
            return self.best_am()
        else:
            return self.INF

    def best_combined_pax(self):
        fastest = self.best_combined() * self.pax_factor()
        if fastest == self.INF:
            return fastest
        else:
            return fastest.quantize(Decimal('.001'))


    def error_in_published(self):
        calculated = self.primary_score()
        msg = f'{self.name} calculated: {calculated}, published: {self.published_primary_score}'

        try:
            if isinstance(self, RallyDriver) and (calculated == 0):
                assert self.DNF_REGEX.match(self.published_primary_score)
            if calculated == self.INF:
                assert self.DNF_REGEX.match(self.published_primary_score)
            elif isinstance(self, TwoCourseDriver) and self.second_half_started:
                # AXWare shows "dns" for two day events if day two has
                # not started. So ignore this
                assert calculated == Decimal(self.published_primary_score)
        except AssertionError:
            print(msg)
            return dict(driver_name=self.name,
                        calculated=float(calculated),
                        published=float(self.published_primary_score))
        except InvalidOperation as exc:
            # We end up here when attempting to parse Decimal('dns')
            print(msg)
            print(f'ERROR parsing scores for {self.name}')
            pdb.set_trace()
            raise exc

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
        props.update(primary_score = str(self.primary_score()),
                     secondary_score = str(self.secondary_score()),
                     #fastest_time = str(self.fastest_time()),
                     #fastest_pax_time = str(self.fastest_pax_time()),
                     pax_factor = str(self.pax_factor()),
                     slug = slug_and_head_shot.get('slug') or '',
                     headshot = slug_and_head_shot.get('head_shot') or '')
        return props

    def primary_score(self):
        return self.best_combined()

    def secondary_score(self):
        return self.best_combined_pax()

class TwoCourseDriver(Driver):
    # The only reason this is here, as opposed to simply using Driver
    # by itself, is so we can use `isinstance` and be specific about
    # a particular subclass
    pass

class OneCourseDriver(Driver):

    def primary_score(self):
        return self.best_run()

    def secondary_score(self):
        return self.best_run_pax()

class RallyDriver(Driver):

    def cumulative(self):
        runs = [run for run in self.runs() if run.strip()]
        score = sum([self.time_from_string(run) for run in runs])
        if not score:
            return self.INF
        return score

    def best_combined_pax(self):
        return None

    def pax_factor(self):
        return None

    def primary_score(self):
        return self.cumulative()

    def secondary_score(self):
        return self.best_run()
