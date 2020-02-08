from pyramid.config import Configurator
from pyramid.static import QueryStringConstantCacheBuster
import time


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')

    # Cache busting of static assets
    # See https://docs.pylonsproject.org/projects/pyramid/en/1.10-branch/narr/assets.html#cache-busting
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_cache_buster('arscca:static/',
                            QueryStringConstantCacheBuster(str(int(time.time()))))

    config.add_route('index', '/')
    # Interesting that /events and /events/ are not the same thing
    config.add_route('events', '/events') # redirects to home
    config.add_route('events_with_slash', '/events/') # redirects to home
    config.add_route('drivers', '/drivers')
    config.add_route('driver', '/drivers/{slug}')
    config.add_route('report', '/standings')
    config.add_route('admin_generate_run_groups', '/admin/run_groups/generate')
    config.add_route('admin_clear_run_groups', '/admin/run_groups/clear')
    config.add_route('admin_run_groups', '/admin/run_groups')
    config.add_route('run_groups', '/run_groups')
    config.add_route('live_event', '/live')
    config.add_route('live_event_raw', '/live/raw')
    config.add_route('live_event_drivers', '/live/drivers')
    config.add_route('live_event_update_redis', '/live/update_redis')
    config.add_route('live_event_revision', '/live/revision')
    config.add_route('event', '/events/{date}')
    config.add_route('photo_upload', '/events/{date}/upload')
    config.add_route('event_photos', '/events/{date}/photos')
    config.add_route('national_event', '/national_events/{year}')
    config.add_route('javascript_errors', '/javascript_errors')
    config.scan()
    return config.make_wsgi_app()

