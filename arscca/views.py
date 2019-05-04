import json
import pdb
import redis
from threading import Lock
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from .models.driver import Driver
from .models.national_event_driver import NationalEventDriver
from .models.parser import Parser

REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
REDIS_EXPIRATION_IN_SECONDS = 3600
LOCK = Lock()

@view_config(route_name='index',
             renderer='templates/index.jinja2')
def home_view(request):
    return dict()



@view_config(route_name='events')
def events_view(request):
    return HTTPFound(location='/')

@view_config(route_name='events_with_slash')
def events_with_slash_view(request):
    return HTTPFound(location='/')


@view_config(route_name='national_event',
             renderer='templates/national_event.jinja2')
def national_event_view(request):
    year = request.matchdict.get('year')
    drivers = [driver.as_dict() for driver in NationalEventDriver.all()]
    event = dict(drivers=drivers,
                 event_name=f'{year} Nationals',
                )

    return event


@view_config(route_name='event',
             renderer='templates/event.jinja2')
def event_view(request):
    date = request.matchdict.get('date')
    event_url = Parser.URLS[date]
    if not event_url:
        request.response.status_code = 404
        return dict(flash=f'No event found for date {date}')

    if request.params.get('cb'):
        # If "cache-buste" param is set, fetch drivers directly
        print('Cache busting')
        json_event = fetch_event(date, event_url)
    else:
        # Otherwise attempt to pull them from cache
        json_event = event_from_redis_or_network_call(date, event_url)

    event = json.loads(json_event)
    return event


# Pull from redis, if available
def event_from_redis_or_network_call(date, url_aka_redis_key):
    json_event = REDIS.get(url_aka_redis_key)
    if json_event:
        print('Serving event cached in Redis')
        return json_event
    else:
        print('Nothing in Redis, so serving event fetched from the Web')
        return populate_redis_and_yield_event(date, url_aka_redis_key)

def populate_redis_and_yield_event(date, url_aka_redis_key):
    # Acquire a lock so that if 100 clients connect at the same time,
    # drivers will only be fetched once
    LOCK.acquire()
    try:
        json_event = REDIS.get(url_aka_redis_key)
        # If lots of request have built up, the first one will populate
        # redis, and the others will find redis populated and return from here
        if json_event:
            return json_event

        generated_json_event = fetch_event(date, url_aka_redis_key)
        REDIS.set(url_aka_redis_key,
                  generated_json_event, ex=REDIS_EXPIRATION_IN_SECONDS)
        return generated_json_event
    finally:
        LOCK.release()

# Fetch directly from other site; Do not read or write to Redis
def fetch_event(date, url):
    parser = Parser(date, url)
    parser.parse()
    parser.rank_drivers()
    drivers_as_dicts = [driver.properties() for driver in parser.drivers]
    event = dict(drivers=drivers_as_dicts,
                 event_name=parser.event_name,
                 event_date=parser.event_date,
                 source_url=url)
    json_event = json.dumps(event)
    return json_event


