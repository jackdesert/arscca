from pyramid.config import Configurator
from pyramid.session import JSONSerializer
from pyramid.static import QueryStringConstantCacheBuster
import time

from pyramid.session import SignedCookieSessionFactory


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')


    # Insecure Session
    # https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html#sessions-chapter
    my_session_factory = SignedCookieSessionFactory('insecure-but-digitally-signed-382746',
                                                    serializer=JSONSerializer())
    config.set_session_factory(my_session_factory)

    # Cache busting of static assets
    # See https://docs.pylonsproject.org/projects/pyramid/en/1.10-branch/narr/assets.html#cache-busting
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_cache_buster('arscca:static/',
                            QueryStringConstantCacheBuster(str(int(time.time()))))

    config.add_route('admin_clear_run_groups', '/admin/run_groups/clear')
    config.add_route('admin_generate_run_groups', '/admin/run_groups/generate')
    config.add_route('admin_run_groups', '/admin/run_groups')
    config.add_route('calendar', '/calendar')
    config.add_route('calendar_slash', '/calendar/')
    config.add_route('calendar_plain', '/calendar/plain')
    config.add_route('exception', '/exception')
    config.add_route('help_index', '/help')
    config.add_route('help_index_slash', '/help/')
    config.add_route('help_show', '/help/{document_name}')
    config.add_route('opinion_index', '/opinion')
    config.add_route('opinion_index_slash', '/opinion/')
    config.add_route('opinion_show', '/opinion/{document_name}')
    config.add_route('driver', '/drivers/{slug}')
    config.add_route('drivers', '/drivers')
    config.add_route('drivers_slash', '/drivers/')
    config.add_route('event', '/events/{date}')
    config.add_route('events', '/events') # redirects to home
    config.add_route('events_slash', '/events/') # redirects to home (slash is distinct)
    config.add_route('index', '/')
    config.add_route('javascript_errors', '/javascript_errors')
    config.add_route('joomla_test__home_page_photos', '/joomla_test/home_page_photos')
    config.add_route('joomla_test__home_page_calendar', '/joomla_test/home_page_calendar')
    config.add_route('live_event', '/live')
    config.add_route('live_event_drivers', '/live/drivers')
    config.add_route('live_event_raw', '/live/raw')
    config.add_route('live_event_revision', '/live/revision')
    config.add_route('live_event_update_redis', '/live/update_redis')
    config.add_route('msreg', '/msreg')
    config.add_route('msreg_upload', '/msreg/upload', request_method='POST')
    config.add_route('msreg_download', '/msreg/{download_filename}', request_method='GET')
    config.add_route('national_event', '/national_events/{year}')
    config.add_route('photo_upload_create', '/photos/upload', request_method='POST')
    config.add_route('photo_upload_new', '/photos/upload', request_method='GET')
    config.add_route('photos', '/photos')
    config.add_route('photos_slash', '/photos/')
    config.add_route('photos__teaser', '/photos/teaser')
    config.add_route('report', '/standings')
    config.add_route('run_groups', '/run_groups')


    config.scan()
    config.include('pyramid_exclog')
    return config.make_wsgi_app()


