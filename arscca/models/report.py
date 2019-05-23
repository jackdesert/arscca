from collections import defaultdict
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
        self._build()

    def events_and_totals(self):
        return (self._events, self._totals)

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
        return keys

    def _build(self):
        # points for each event separately
        # used for filling in the table
        events = dict()

        # points for all events together
        # -- uses a defaultdict with inner defaultdict(int) --
        totals = defaultdict(lambda: defaultdict(int))

        for key in self._redis_keys():
            json_data = self.REDIS.get(key)
            data_for_one_event = json.loads(json_data)
            date = key.replace(self.KEY_PREPEND, '')
            events[date] = data_for_one_event
            for pax_or_car_class, nested_data in data_for_one_event.items():
                for driver_name, points in nested_data.items():
                    totals[pax_or_car_class][driver_name] += points
        self._totals = totals
        self._events = events




if __name__ == '__main__':
    rep = Report('2019')
    print(rep._redis_keys())
    events, totals = rep.events_and_totals()
    pdb.set_trace()
    5


