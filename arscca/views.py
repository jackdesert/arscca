import json
import pdb
import redis
from threading import Lock
from pyramid.view import view_config
from .models.driver import Driver
from .models.parser import Parser

REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
REDIS_EXPIRATION_IN_SECONDS = 3600
LOCK = Lock()

@view_config(route_name='home',
             renderer='templates/mytemplate.jinja2')
def my_view(request):
    url = 'http://arscca.org/index.php?option=com_content&view=article&id=398:2018-solo-ii-event-6-final&catid=125&Itemid=103'

    if request.params.get('cb'):
        # If "cache-buste" param is set, fetch drivers directly
        print('Cache busting')
        json_drivers = fetch_drivers(url)
    else:
        # Otherwise attempt to pull them from cache
        json_drivers = drivers_from_redis_or_network_call(url)

    return dict(drivers=json_drivers)


# Pull from redis, if available
def drivers_from_redis_or_network_call(url_aka_redis_key):
    json_drivers = REDIS.get(url_aka_redis_key)
    if json_drivers:
        print('Serving drivers cached in Redis')
        return json_drivers
    else:
        print('Nothing in Redis, so serving drivers fetched from the Web')
        return populate_redis_and_yield_drivers(url_aka_redis_key)

def populate_redis_and_yield_drivers(url_aka_redis_key):
    # Acquire a lock so that if 100 clients connect at the same time,
    # drivers will only be fetched once
    LOCK.acquire()
    try:
        json_drivers = REDIS.get(url_aka_redis_key)
        # If lots of request have built up, the first one will populate
        # redis, and the others will find redis populated and return from here
        if json_drivers:
            return json_drivers

        generated_json_drivers = fetch_drivers(url_aka_redis_key)
        REDIS.set(url_aka_redis_key,
                  generated_json_drivers, ex=REDIS_EXPIRATION_IN_SECONDS)
        return generated_json_drivers
    finally:
        LOCK.release()

# Fetch directly from other site; Do not read or write to Redis
def fetch_drivers(url):
    parser = Parser(url)
    parser.parse()
    parser.rank_drivers()
    drivers_as_dicts = [driver.properties() for driver in parser.drivers]
    json_drivers = json.dumps(drivers_as_dicts)
    return json_drivers
