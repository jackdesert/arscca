import json
import pdb
from arscca.models.canon import Canon
from arscca.models.shared import Shared
from collections import defaultdict
from datetime import datetime

class FondMemory:

    REDIS = Shared.REDIS
    REDIS_KEY_PREPEND = 'fond-memories'
    REDIS_KEY_EVENT_DATES = 'fond-memories-event-dates'
    REDIS_KEY_EVENT_NAMES = 'fond-memories-event-names'

    def __init__(self, driver, event_date):
        self._driver = driver
        self._event_date = event_date

    def write(self):
        self.REDIS.set(self.__redis_key,
                       json.dumps(self.__data))

        # Add the event date to a redis set
        self.REDIS.sadd(self.REDIS_KEY_EVENT_DATES, self._event_date)

    @property
    def __redis_key(self):
        driver_slug = Canon(self._driver.name).slug
        key = f'{self.REDIS_KEY_PREPEND}--{driver_slug}--{self._event_date}'
        return key

    @property
    def __redis_key_events_per_year(self):
        year = self._event_date[0:4]
        key = f'{self.REDIS_KEY_PREPEND_EVENTS_PER_YEAR}--{driver_slug}--{self._event_date}'
        return key

    @property
    def __data(self):
        if hasattr(self._driver, 'percentile_rank'):
            pr = self._driver.percentile_rank
        else:
            pr = None

        payload = {'event_date': self._event_date, # This is duplicated in the key
                   'car_model': self._driver.car_model,
                   'percentile_rank': pr}
        return payload

    @classmethod
    def all_for_driver(cls, driver_slug):
        output = {}
        keys = cls._all_keys_for_driver(driver_slug)

        # Sort the keys
        json_blobs = cls.REDIS.mget(sorted(keys))
        for json_blob in json_blobs:
            blob = json.loads(json_blob)
            event_date = blob['event_date']
            output[event_date] = blob

        return output

    @classmethod
    def _all_keys_for_driver(cls, driver_slug):

        match = f'{cls.REDIS_KEY_PREPEND}--{driver_slug}--*'
        keys = set()
        cursor = 0
        while True:
            cursor, matching_keys = cls.REDIS.scan(cursor=cursor, match=match)
            for key in matching_keys:
                keys.add(key)
            if cursor == 0:
                break
        return keys



    # Event names are stored so they can be used on the front page
    @classmethod
    def store_event_name(cls, date, event_name):
        event_name = event_name.strip()
        cls.REDIS.hset(cls.REDIS_KEY_EVENT_NAMES, date, event_name)

    @classmethod
    def event_names(cls):
        return cls.REDIS.hgetall(cls.REDIS_KEY_EVENT_NAMES)



if __name__ == '__main__':
    keys = FondMemory._all_keys_for_driver('jack_desert')
    print(keys)

    FondMemory.all_for_driver('jack_desert')


