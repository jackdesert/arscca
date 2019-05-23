from collections import defaultdict
from copy import deepcopy
import json
import pdb
import redis

class Report:
    REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
    KEY_PREPEND = 'points-from-'

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
        klasses.remove('PAX')
        output = ['PAX']
        for klass in sorted(klasses):
            output.append(klass)
        return output

    @property
    def num_events(self):
        return self._num_events

    @property
    def _redis_key_prepend(self):
        return f'{self.KEY_PREPEND}{self.year}*'

    def _redis_keys(self):
        keys = set()
        cursor = 0
        while True:
            cursor, items = self.REDIS.scan(cursor=cursor, match=self._redis_key_prepend)
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
            json_data = self.REDIS.get(key)
            data_for_one_event = json.loads(json_data)
            date = key.replace(self.KEY_PREPEND, '')
            events[date] = data_for_one_event
            for pax_or_car_class, nested_data in data_for_one_event.items():
                for driver_name, points in nested_data.items():
                    self._car_classes.add(pax_or_car_class)
                    totals[pax_or_car_class][driver_name].append(points)
        self._totals = totals
        self._events = events

    def _sum_best_n(self, scores):
        scores = sorted(scores, reverse=True)
        num_events_to_score = self.num_events - 2
        scores_to_use = [score for score, _ in zip(scores, range(num_events_to_score))]
        summed = sum(scores_to_use)
        return summed




if __name__ == '__main__':
    rep = Report('2019')
    print(rep._redis_keys())
    events, totals = rep.events_and_totals()
    pdb.set_trace()
    5


