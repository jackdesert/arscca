import json
import logging
import pdb
import redis

from arscca.models.histogram import Histogram
from arscca.models.live_event_presenter import LiveEventPresenter
from arscca.models.national_event_driver import NationalEventDriver
from arscca.models.parser import Parser
from arscca.models.parser import StandardParser
from arscca.models.photo import Photo
from arscca.models.shared import Shared
from arscca.models.short_queue import ShortQueue
from arscca.models.report import Report
from arscca.models.timer import Timer
from datetime import date as Date
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from threading import Lock

REDIS = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
REDIS_EXPIRATION_IN_SECONDS = 3600
LOCK = Lock()
LIVE_UPDATE_LOCK = Lock()
LIVE_UPDATE_QUEUE = ShortQueue()
LOG = logging.getLogger(__name__)

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


@view_config(route_name='live_event_drivers',
             renderer='json')
def live_event_drivers_view(request):
    output_json = REDIS.get(Shared.REDIS_KEY_LIVE_EVENT_DRIVERS)
    output = json.loads(output_json)

    # Send a requiest timestamp so client can compare
    # revision timestamps truthfully
    output['request_timestamp'] = datetime.now().isoformat()

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

    if not LIVE_UPDATE_QUEUE.join():
        # If you run the demo with less delay in between each update
        # than it takes the server to process them, they will stack up.
        # The LIVE_UPDATE_QUEUE allows us to drop excess requests
        # But still ensure that the last thing changed gets registered
        LOG.warn('Live Update returning 429 because a request is already waiting')
        request.response.status_code = 429
        return {}

    # Only allow one thread to use this method at a time
    # Otherwise, revision may be out of sync between
    # event(includes revision), drivers_and_revision, and revision
    LIVE_UPDATE_LOCK.acquire()
    LIVE_UPDATE_QUEUE.leave()
    timer = Timer()

    try:
        # This event_json includes the updated revision
        event_json = fetch_event(date, event_url, True)
        event = json.loads(event_json)
        drivers_json = event['drivers_json']
        drivers = json.loads(drivers_json)
        revision = int(event['revision'])
        revision_timestamp = datetime.now().isoformat()

        drivers_and_revision = dict(drivers=drivers,
                                    revision=revision,
                                    revision_timestamp=revision_timestamp)

        drivers_and_revision_json = json.dumps(drivers_and_revision)

        previous_event_json = REDIS.get(Shared.REDIS_KEY_LIVE_EVENT) or '{"drivers_json": "[]"}'
        previous_event = json.loads(previous_event_json)
        previous_drivers_json = previous_event['drivers_json']
        previous_drivers = json.loads(previous_drivers_json)

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
        REDIS.set(Shared.REDIS_KEY_LIVE_EVENT, event_json)
        REDIS.set(Shared.REDIS_KEY_LIVE_EVENT_DRIVERS, drivers_and_revision_json)
        REDIS.incr(Shared.REDIS_KEY_LIVE_EVENT_REVISION)

        LOG.warn(f'Live Update returning 200 with elapsed: {timer.elapsed}')
        return dict(revision=revision,
                    revision_timestamp=revision_timestamp,
                    driver_changes=drivers_diff)
    finally:
        LIVE_UPDATE_LOCK.release()



@view_config(route_name='live_event',
             renderer='templates/event.jinja2')
def live_event_view(request):
    # this method reads data from redis
    date = str(Date.today())
    event_url = '/live/raw'

    event_json = REDIS.get(Shared.REDIS_KEY_LIVE_EVENT)

    #try:
    #    event_json = fetch_event(date, event_url, True)
    #except:
    #    # If any errors occur, serve them the raw data instead
    #    request.override_renderer = Parser.LIVE_FILENAME
    #    return {}

    event = json.loads(event_json) # If TypeError, no event stored in redis
    return event

@view_config(route_name='live_event_raw',
             renderer=StandardParser.LIVE_FILENAME)
def live_event_raw_view(request):
    return {}

@view_config(route_name='event',
             renderer='templates/event.jinja2')
def event_view(request):
    date = request.matchdict.get('date')
    event_url = StandardParser.URLS.get(date)
    if not event_url:
        request.response.status_code = 404
        request.override_renderer = 'static/404.jinja2'
        return {}

    if request.params.get('cb'):
        # If "cache-buste" param is set, fetch drivers directly
        print('Cache busting')
        event_json = fetch_event(date, event_url)
    else:
        # Otherwise attempt to pull them from cache
        event_json = event_from_redis_or_network_call(date, event_url)

    event = json.loads(event_json)
    return event


# Pull from redis, if available
def event_from_redis_or_network_call(date, url_aka_redis_key):
    event_json = REDIS.get(url_aka_redis_key)
    if event_json:
        print('Serving event cached in Redis')
        return event_json
    else:
        print('Nothing in Redis, so serving event fetched from the Web')
        return populate_redis_and_yield_event(date, url_aka_redis_key)

def populate_redis_and_yield_event(date, url_aka_redis_key):
    # Acquire a lock so that if 100 clients connect at the same time,
    # drivers will only be fetched once
    LOCK.acquire()
    try:
        event_json = REDIS.get(url_aka_redis_key)
        # If lots of request have built up, the first one will populate
        # redis, and the others will find redis populated and return from here
        if event_json:
            return event_json

        generated_event_json = fetch_event(date, url_aka_redis_key)
        REDIS.set(url_aka_redis_key,
                  generated_event_json, ex=REDIS_EXPIRATION_IN_SECONDS)
        return generated_event_json
    finally:
        LOCK.release()

# Fetch directly from other site; Do not read or write to Redis
def fetch_event(date, url, live=False):
    parser = Parser.instantiate_correct_type(date, url, live)
    parser.parse()
    parser.rank_drivers()

    errors = []
    for driver in parser.drivers:
        error = driver.error_in_published()
        if error:
            errors.append(error)

    histogram_filename = None
    histogram_conformed_count = None
    if not live:
        histogram = Histogram(parser.drivers)
        histogram.plot()
        histogram_filename = histogram.filename
        histogram_conformed_count = histogram.conformed_count

    drivers_as_dicts = [driver.properties() for driver in parser.drivers]
    drivers_json = json.dumps(drivers_as_dicts)
    runs_per_driver = parser.NUM_COURSES * parser.runs_per_course
    num_courses = parser.NUM_COURSES

    event = dict(drivers_json=drivers_json,
                 event_name=parser.event_name,
                 event_date=parser.event_date,
                 source_url=url,
                 live=live,
                 histogram_filename=histogram_filename,
                 histogram_conformed_count=histogram_conformed_count,
                 runs_per_driver=runs_per_driver,
                 num_courses=num_courses,
                 errors=errors)
    if live:
        # Set revision but do not increment in REDIS
        old_revision = REDIS.get(Shared.REDIS_KEY_LIVE_EVENT_REVISION) or 0
        event['revision'] = int(old_revision) + 1
    event_json = json.dumps(event)
    return event_json



