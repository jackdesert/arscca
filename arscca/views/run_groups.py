import json
import os
import pdb
import redis

from arscca.models.canon import Canon
from arscca.models.util import Util
from arscca.models.shared import Shared
from collections import defaultdict
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

REDIS = Shared.REDIS




# These two views are almost identical
@view_config(route_name='run_groups',
             renderer='templates/run_groups.jinja2')
def run_groups_view(request):
    redis_data_json = REDIS.get(Shared.REDIS_KEY_LIVE_EVENT_RUN_GROUPS)
    redis_data = {}
    if redis_data_json:
        redis_data = json.loads(redis_data_json)
    return redis_data

@view_config(route_name='admin_run_groups',
             renderer='templates/run_groups.jinja2')
def admin_run_groups_view(request):
    redis_data_json = REDIS.get(Shared.REDIS_KEY_LIVE_EVENT_RUN_GROUPS)
    redis_data = {}
    if redis_data_json:
        redis_data = json.loads(redis_data_json)

    redis_data['admin'] = True
    return redis_data




@view_config(route_name='admin_clear_run_groups',
             renderer='templates/run_groups.jinja2')
def admin_clear_run_groups_view(request):
    REDIS.delete(Shared.REDIS_KEY_LIVE_EVENT_RUN_GROUPS)

    return HTTPFound(location='/admin/run_groups')

@view_config(route_name='admin_generate_run_groups',
             renderer='templates/run_groups.jinja2')
def admin_generate_run_groups_view(request):
    drivers_etc_json = REDIS.get(Shared.REDIS_KEY_LIVE_EVENT_DRIVERS)
    drivers_etc = json.loads(drivers_etc_json)
    data = defaultdict(list)
    drivers = drivers_etc['drivers']
    for driver in drivers:
        driver_name = driver['name']
        car_class = driver['car_class']
        driver_slug = Canon(driver_name).slug
        data[car_class].append((driver_name, driver_slug))

    run_groups, counter = Util.randomize_run_groups(data)

    axware_capable_slugs = []
    if _slugs := os.getenv('ARSCCA_AXWARE_CAPABLE'):
        axware_capable_slugs = _slugs.split(',')

    redis_data = dict(run_groups=run_groups,
                      axware_capable_slugs=axware_capable_slugs,
                      counter=counter,
                      num_drivers=len(drivers))


    REDIS.set(Shared.REDIS_KEY_LIVE_EVENT_RUN_GROUPS, json.dumps(redis_data))
    return HTTPFound(location='/admin/run_groups')

