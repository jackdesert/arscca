import hashlib
import json
import pdb
import redis
from datetime import date as Date
from threading import Lock
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from .models.driver import Driver
from .models.gossip import Gossip
from .models.histogram import Histogram
from .models.live_event_presenter import LiveEventPresenter
from .models.national_event_driver import NationalEventDriver
from .models.parser import Parser
from .models.photo import Photo
from .models.report import Report

REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
REDIS_EXPIRATION_IN_SECONDS = 3600
LOCK = Lock()
LIVE_UPDATE_LOCK = Lock()

REDIS_KEY_LIVE_EVENT          = 'live-event'
REDIS_KEY_LIVE_EVENT_DRIVERS  = 'live-event-drivers'
REDIS_KEY_LIVE_EVENT_REVISION = 'live-event-revision'

@view_config(route_name='index',
             renderer='templates/index.jinja2')
def home_view(request):
    photos = Photo.all()
    return dict(photos=photos)



@view_config(route_name='events')
def events_view(request):
    return HTTPFound(location='/')

@view_config(route_name='events_with_slash')
def events_with_slash_view(request):
    return HTTPFound(location='/')


@view_config(route_name='drivers',
             renderer='templates/drivers.jinja2')
def drivers_view(request):
    photos = Photo.all()
    return dict(photos=photos)

@view_config(route_name='driver',
             renderer='templates/driver.jinja2')
def driver_view(request):
    slug = request.matchdict.get('slug')
    gossip = Gossip(slug)

    name = slug.replace('_', ' ').title()
    photos = Photo.all_for_driver(slug)

    return dict(name=name, photos=photos, gossip=gossip.html())

@view_config(route_name='report',
             renderer='templates/report.jinja2')
def report_view(request):
    year = 2019
    report = Report(year)
    events, totals = report.events_and_totals()

    return dict(events=events,
                totals=totals,
                car_classes=report.car_classes,
                event_numbers=report.event_numbers,
                year=year,
                slug_and_head_shot_method=Photo.slug_and_head_shot)

@view_config(route_name='national_event',
             renderer='templates/national_event.jinja2')
def national_event_view(request):
    year = request.matchdict.get('year')
    drivers = [driver.as_dict() for driver in NationalEventDriver.all(year)]
    event = dict(drivers=drivers,
                 year=year)
    return event


@view_config(route_name='live_event_revision',
             renderer='json')
def live_event_revision_view(request):
    revision = REDIS.get(REDIS_KEY_LIVE_EVENT_REVISION)
    return dict(revision=revision)

@view_config(route_name='live_event_drivers',
             renderer='json')
def live_event_drivers_view(request):
    json_output = REDIS.get(REDIS_KEY_LIVE_EVENT_DRIVERS)
    output = json.loads(json_ouput)

    # It's extra work to call json.loads on the redis data
    # and then expect the renderer to turn it back into json.
    # But at least it sets the Content-Type to application/json for us
    return output


@view_config(route_name='live_event_update_redis',
             renderer='json')
def live_event_update_redis_view(request):
    # This method is called by the gingerbread man
    # when Parser.LIVE_FILENAME is updated
    # This method writes data to redis
    # and returns a diff
    #
    # live_event_view, on the other hand, only reads data from redis
    # (does not read from file at all)

    date = str(Date.today())
    event_url = '/live/raw'

    # Only allow one thread to use this method at a time
    # Otherwise, revision may be out of sync between
    # event(includes revision), drivers_and_revision, and revision
    LIVE_UPDATE_LOCK.acquire()

    try:
        # This json_event includes the updated revision
        json_event = fetch_event(date, event_url, True)
        event = json.loads(json_event)
        json_drivers = event['drivers']
        drivers = json.loads(json_drivers)
        revision = event['revision']

        drivers_and_revision = dict(drivers=drivers,
                                    revision=revision)

        json_drivers_and_revision = json.dumps(drivers_and_revision)

        json_previous_event = REDIS.get(REDIS_KEY_LIVE_EVENT) or '{"drivers": []}'
        previous_event = json.loads(json_previous_event)
        previous_drivers = previous_event['drivers']
        pdb.set_trace()

        drivers_diff = LiveEventPresenter.diff(previous_drivers, drivers)

        # Ideally, these three writes to redis would be atomic
        # But since we have a Lock on this view method,
        # and this is the only method that writes to these redis keys,
        # we are probably fine.
        #
        # There is such a thing as redis transactions,
        # But I did not find any documentation of that feature
        # for the redis-py package that this project uses.
        #
        # Therefore, all dicts are converted to json strings
        # above so that if there are any errors they will likely
        # happen BEFORE these three lines
        REDIS.set(REDIS_KEY_LIVE_EVENT, json_event)
        REDIS.set(REDIS_KEY_LIVE_EVENT_DRIVERS, json_drivers_and_revision)
        REDIS.incr(REDIS_KEY_LIVE_EVENT_REVISION)


        return dict(revision=revision,
                    drivers=drivers_diff)
    finally:
        LIVE_UPDATE_LOCK.release()



@view_config(route_name='live_event',
             renderer='templates/event.jinja2')
def live_event_view(request):
    # this method reads data from redis
    date = str(Date.today())
    event_url = '/live/raw'

    json_event = REDIS.get(url_aka_redis_key)

    try:
        json_event = fetch_event(date, event_url, True)
    except:
        # If any errors occur, serve them the raw data instead
        request.override_renderer = Parser.LIVE_FILENAME
        return {}

    event = json.loads(json_event)
    return event

@view_config(route_name='live_event_raw',
             renderer=Parser.LIVE_FILENAME)
def live_event_raw_view(request):
    return {}

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
def fetch_event(date, url, live=False):
    parser = Parser(date, url, live)
    parser.parse()
    parser.rank_drivers()

    errors = []
    for driver in parser.drivers:
        error = driver.error_in_best_combined()
        if error:
            errors.append(error)

    histogram = Histogram(parser.drivers)
    histogram.plot()

    drivers_as_dicts = [driver.properties() for driver in parser.drivers]
    drivers_as_json = json.dumps(drivers_as_dicts)
    runs_per_driver = 2 * parser.runs_per_course

    event = dict(drivers=drivers_as_json,
                 event_name=parser.event_name,
                 event_date=parser.event_date,
                 source_url=url,
                 live=live,
                 histogram_filename=histogram.filename,
                 runs_per_driver=runs_per_driver,
                 errors=errors)
    if live:
        # Set revision but do not increment in REDIS
        old_revision = REDIS.get(REDIS_KEY_LIVE_EVENT_REVISION) or 0
        event['revision'] = old_revision + 1
    json_event = json.dumps(event)
    return json_event



