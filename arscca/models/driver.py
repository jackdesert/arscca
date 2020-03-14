import pdb
import re
from arscca.models.canon import Canon
from arscca.models.shared import Shared
from decimal import Decimal
from decimal import InvalidOperation
from .pax import Pax
from .photo import Photo

class GenericDriver:
    DNF_REGEX     = re.compile(r'(dnf)|(dns)|(dsq)', re.IGNORECASE)
    TIME_AND_PENALTY_REGEX = re.compile(r'([0-9.]+)(\+(\d)(/(\d))?)?')
    INF           = Decimal('inf')

    PYLON_PENALTY_IN_SECONDS = 2
    MISSED_GATE_PENALTY_IN_SECONDS = 10


    def __init__(self, year, row_1, row_2, first_run_column, published_primary_score_column):
        self.year = year
        self._row_1 = row_1
        self._row_2 = row_2
        self._first_run_column = first_run_column
        self._published_primary_score_column = published_primary_score_column
        # See Parser.parse() for a list of instance variables stored on Driver


    @property
    def car_class(self):
        return self._row_1[1]

    @property
    def car_number(self):
        return self._row_1[2]

    @property
    def name(self):
        return Canon(self._row_1[3]).name

    @property
    def car_model(self):
        return self._row_1[4]

    @property
    def id(self):
        return f'{self.driver_slug}--{self.car_class}_{self.car_number}'

    @property
    def driver_slug(self):
        return Canon(self.name).slug

    @property
    def published_primary_score(self):
        return self._row_1[self._published_primary_score_column]


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
            raise RuntimeError(f'Unable to parse time_from_string("{string}")')

        return time + pylon_penalty + gate_penalty

    def _best_of_n(self, runs):
        runs_to_use = [rr for rr in runs if rr.strip()]
        times = [self.time_from_string(rr) for rr in runs_to_use]
        if times:
            return min(times)

    def _runs_upper(self):
        return self._row_1[self._first_run_column : self._published_primary_score_column]

    def _runs_lower(self):
        if not self._row_2:
            return tuple()
        return self._row_2[self._first_run_column : self._published_primary_score_column]

    def runs(self):
        return self._runs_upper() + self._runs_lower()

    def num_completed_runs_upper(self):
        return self._num_completed(self._runs_upper())

    def num_completed_runs_lower(self):
        return self._num_completed(self._runs_lower())

    def _num_completed(self, runs):
        count = 0
        for run in runs:
            if Shared.NOT_JUST_WHITESPACE_REGEX.search(run):
                count += 1
        return count









    def error_in_published(self):
        calculated = self.primary_score()
        msg = f'{self.name} calculated: {calculated}, published: {self.published_primary_score}'

        try:
            if isinstance(self, RallyDriver) and (calculated == 0):
                if not self.DNF_REGEX.match(self.published_primary_score):
                    raise AssertionError
            if calculated == self.INF:
                if not self.DNF_REGEX.match(self.published_primary_score):
                    raise AssertionError
            elif isinstance(self, TwoCourseDriver) and self.second_half_started:
                # AXWare shows "dns" for two day events if day two has
                # not started. So we only make the following assertion
                # if the second half has actually started
                #
                # In the case of 2012-11-04, there are DNS where they don't belong
                # So test for DNS first before instantiating a Decimal()
                if not str(calculated) == self.published_primary_score.strip():
                    raise AssertionError
        except AssertionError:
            try: pub = float(self.published_primary_score)
            except ValueError: pub = self.published_primary_score

            print(msg)
            return dict(driver_name=self.name,
                        calculated=float(calculated),
                        published=pub)
        except InvalidOperation as exc:
            # We end up here when attempting to parse Decimal('dns')
            print(msg)
            print(f'ERROR parsing scores for {self.name}')
            pdb.set_trace()
            raise exc

    def __repr__(self):
        return f'{type(self)}: {self.name}'

    # This is useful for development purposes
    def print(self):
        print('')
        print(f'name            {self.name}')
        print(f'car_number      {self.car_number}')
        print(f'car_class       {self.car_class}')
        print(f'car_model       {self.car_model}')
        print(f'_upper_runs      {self._upper_runs()}')
        print(f'_lower_runs      {self._lower_runs()}')
        print(f'primary_score   {self.primary_score()}')
        print(f'secondary_score {self.secondary_score()}')

    # max_runs_upper and max_runs_lower are used
    # to trim off blank runs so that it displays
    # beautifully in HTML
    def properties(self, max_runs_upper=None, max_runs_lower=None):
        slug_and_head_shot = Photo.slug_and_head_shot(self.name)

        props = self.__dict__.copy()

        # Delete these foundational rows since we break the important data
        # out by separate keys
        del props['_first_run_column']
        del props['_published_primary_score_column']
        del props['_row_1']
        del props['_row_2']

        props.update(id = self.id,
                     name = self.name,
                     car_class = self.car_class,
                     car_model = self.car_model,
                     car_number = self.car_number,
                     primary_score = str(self.primary_score()),
                     secondary_score = str(self.secondary_score()),
                     published_primary_score = str(self.published_primary_score),
                     # Note that [1,2][0:None] returns [1,2]
                     runs_upper = self._runs_upper()[0:max_runs_upper],
                     runs_lower = self._runs_lower()[0:max_runs_lower],
                     pax_factor = str(self.pax_factor()),
                     slug = slug_and_head_shot.get('slug') or '',
                     headshot = slug_and_head_shot.get('head_shot') or '')
        return props

    def primary_score(self):
        raise NotImplementedError

    def secondary_score(self):
        raise NotImplementedError



    def best_run(self):
        # This method is only useful to OneCourseDrivers and RallyDrivers
        if isinstance(self, TwoCourseDriver):
            raise NotImplementedError

        runs = self.runs()
        return self._best_of_n(runs) or self.INF

class TwoCourseDriver(GenericDriver):


    def primary_score(self):
        return self.best_combined()

    def secondary_score(self):
        return self.best_combined_pax()

    def best_am(self):
        return self._best_of_n(self._runs_upper())

    def best_pm(self):
        return self._best_of_n(self._runs_lower())

    def best_combined(self):
        if self.best_am() and not self.second_half_started:
            return self.best_am()
        elif self.second_half_started and self.best_am() and self.best_pm():
            return self.best_am() + self.best_pm()
        else:
            return self.INF

    def best_combined_pax(self):
        fastest = self.best_combined() * self.pax_factor()
        if fastest == self.INF:
            return fastest
        else:
            return fastest.quantize(Decimal('.001'))

class OneCourseDriver(GenericDriver):

    def primary_score(self):
        return self.best_run()

    def secondary_score(self):
        return self.best_run_pax()


    def best_run_pax(self):
        best = self.best_run() * self.pax_factor()
        if best == self.INF:
            return best
        else:
            return best.quantize(Decimal('.001'))

class RallyDriver(GenericDriver):


    def cumulative(self):
        runs = [run for run in self.runs() if run.strip()]
        score = sum([self.time_from_string(run) for run in runs])
        if not score:
            return self.INF
        return score

    def pax_factor(self):
        return None

    def primary_score(self):
        return self.cumulative()

    def secondary_score(self):
        return self.best_run()
