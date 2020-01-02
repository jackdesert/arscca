from arscca.models.canon import Canon
from arscca.models.fond_memory import FondMemory
from arscca.models.driver import GenericDriver
from arscca.models.log_splitter import LogSplitter
from arscca.models.shared import Shared
from arscca.models.util import Util
from collections import defaultdict
import json
import pdb
import re

class Dispatcher:


    # This filename ends in jinja2 because it is used as a view template
    LIVE_FILENAME = '/home/arscca/arscca-live.jinja2'

    # You only need to fill this out for the current year,
    # since that is the only year that requires point calculation
    NON_POINTS_EVENT_DATES = ['2019-12-08']

    PAX_STRING = 'PAX'


    def __init__(self, date, url, live):
        self.date = date
        self.url = url
        self.live = live # Boolean
        self._point_storage = defaultdict(int)

        # Several things are delegated to LogSplitter
        self._log_splitter = LogSplitter(date, url, live)
        # self.drivers will be an array
        # self.event_name will be a string
        # self.data will be a list

    def compile(self):
        self.drivers = self._log_splitter.build_and_return_drivers()
        self._set_second_half_started_on_drivers()
        self._rank_drivers()
        self._apply_points()

    def _set_second_half_started_on_drivers(self):

        second_half_started = False
        # StandardParser uses two rows to represent a single driver
        # BestTimeParser uses one row  to represent a single driver
        for driver in self.drivers:
            if driver.best_pm() and not Util.KART_KLASS_REGEX.match(driver.car_class):
                # Second half is triggered when a non-kart-driver has afternoon score
                second_half_started = True

        # delete driver to prevent leakage into second loop
        del driver

        for driver in self.drivers:
            driver.second_half_started = second_half_started

    def _rank_drivers(self):

        scores = [driver.primary_score() for driver in self.drivers]
        num_drivers = len([score for score in scores if score < GenericDriver.INF])

        self.drivers.sort(key=self._log_splitter.driver_type.secondary_score)
        for index, driver in enumerate(self.drivers):
            if driver.best_combined() < GenericDriver.INF:
                driver.secondary_rank = index + 1

        if not self.live:
            self._apply_points()

        self.drivers.sort(key=self._log_splitter.driver_type.primary_score)
        for index, driver in enumerate(self.drivers):
            if driver.best_combined() < GenericDriver.INF:
                driver.primary_rank = index + 1
                driver.percentile_rank = round(100 * index / num_drivers)

        if not self.live:
            self._create_fond_memories()

        self.drivers.sort(key=GenericDriver.car_class_sortable)
        rank = 1
        last_car_class = self.drivers[0].car_class
        for driver in self.drivers:
            if driver.car_class != last_car_class:
                rank = 1
            driver.class_rank = rank
            rank += 1
            last_car_class = driver.car_class


    def _create_fond_memories(self):
        FondMemory.store_event_name(self.date, self.event_name)
        for driver in self.drivers:
            memory = FondMemory(driver, self.date)
            memory.write()

    def _apply_points(self):
        if self.date in self.NON_POINTS_EVENT_DATES:
            # Test & Tune, Hangover generally not pointed
            return

        data = defaultdict(dict)
        for index, driver in enumerate(self.drivers):
            canonical_driver_name = Canon(driver.name).name

            if driver.best_combined() == GenericDriver.INF:
                # No points unless you scored
                print(f'{canonical_driver_name} did not score')
                continue
            pax_points = self._point(self.PAX_STRING)
            if pax_points > 0:
                data[self.PAX_STRING][canonical_driver_name] = pax_points
            car_class = driver.car_class.lower()
            car_class_points = self._point(car_class)
            if car_class_points > 0:
                data[car_class][canonical_driver_name] = car_class_points
            print(f'{canonical_driver_name} awarded {pax_points} pax points and {car_class_points} {car_class} points')
        Shared.REDIS.set(f'points-from-{self.date}', json.dumps(data))

    def _point(self, pax_or_car_class):
        num_drivers_ahead = self._point_storage[pax_or_car_class]
        if num_drivers_ahead == 0 and (pax_or_car_class != self.PAX_STRING):
            points = 11
        else:
            points = 10 - num_drivers_ahead

        # points do not go lower than zero
        points = max([0, points])

        self._point_storage[pax_or_car_class] += 1

        return points

    def max_runs_per_driver_upper(self):
        # This is used by the view
        return max([driver.num_completed_runs_upper() for driver in self.drivers])

    def max_runs_per_driver_lower(self):
        # This is used by the view
        return max([driver.num_completed_runs_lower() for driver in self.drivers])

    @property
    def event_helper(self):
        return self._log_splitter.event_helper

    @property
    def event_name(self):
        return self._log_splitter.event_name
