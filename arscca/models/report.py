from arscca.models.canon import Canon
from arscca.models.shared import Shared
from arscca.models.util import Util
from collections import defaultdict
from copy import deepcopy
import json
import pdb
import redis


class Report:

    KEY_PREPEND = 'points-from-'

    # Each year you must update how many events to drop
    # (But shown here in the inclusive)
    NUM_EVENTS_TO_SCORE = 13
    SKIPPED_EVENT_NUMBERS = defaultdict(list)

    # SKIPPED EVENTS means the event did not happen
    SKIPPED_EVENT_NUMBERS[2019] = [3, 7, 11]
    SKIPPED_EVENT_NUMBERS[2020] = [2, 3, 4]

    # Events that happened, but receive no points
    # You only need to fill this out for the current year,
    # since that is the only year that requires point calculation
    NON_POINTS_EVENT_DATES = frozenset(['2019-12-08', '2020-03-07'])

    def __init__(self, year):
        self.year = year
        self._totals = None
        self._events = None
        self._car_classes = set()
        self._num_events = None
        self._build()

    def events_and_totals(self):
        aggregate_totals = deepcopy(self._totals)
        for car_class, data in aggregate_totals.items():
            for driver_name, scores in data.items():
                data[driver_name] = self._sum_best_n(scores)
        return (self._events, aggregate_totals)

    # Some events may not have all car classes,
    # so we build up a set of all car classes from all events
    @property
    def car_classes(self):
        klasses = self._car_classes.copy()
        if not klasses:
            # Return gracefully if no events yet
            return []
        klasses.remove('PAX')
        output = ['PAX']
        for klass in sorted(klasses):
            output.append(klass)
        return output

    @property
    def num_events(self):
        return self._num_events

    @property
    def event_numbers(self):
        skipped_event_numbers = self.SKIPPED_EVENT_NUMBERS[self.year]
        return Util.range_with_skipped_values(self.num_events, skipped_event_numbers)

    @property
    def _redis_key_prepend(self):
        return f'{self.KEY_PREPEND}{self.year}*'

    def _redis_keys(self):
        keys = set()
        cursor = 0
        while True:
            cursor, items = Shared.REDIS.scan(
                cursor=cursor, match=self._redis_key_prepend
            )
            for item in items:
                keys.add(item)
            if cursor == 0:
                break
        self._num_events = len(keys)
        return keys

    def _build(self):
        # points for each event separately
        # used for filling in the table
        events = dict()

        # points for all events together
        # -- uses a defaultdict with inner defaultdict(int) --
        totals = defaultdict(lambda: defaultdict(list))

        for key in self._redis_keys():
            json_data = Shared.REDIS.get(key)
            data_for_one_event = json.loads(json_data)
            date = key.replace(self.KEY_PREPEND, '')
            events[date] = data_for_one_event
            for pax_or_car_class, nested_data in data_for_one_event.items():
                for driver_name, points in nested_data.items():
                    canonical_driver_name = Canon(driver_name).name
                    self._car_classes.add(pax_or_car_class)
                    totals[pax_or_car_class][canonical_driver_name].append(points)
        self._totals = totals
        self._events = events

    def _sum_best_n(self, scores):
        scores = sorted(scores, reverse=True)
        scores_to_use = [
            score for score, _ in zip(scores, range(self.NUM_EVENTS_TO_SCORE))
        ]
        summed = sum(scores_to_use)
        return summed


if __name__ == '__main__':
    rep = Report('2019')
    print(rep._redis_keys())
    events, totals = rep.events_and_totals()
    pdb.set_trace()
    1
