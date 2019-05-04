from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')

    # Interesting that /events and /events/ are not the same thing
    config.add_route('events', '/events') # redirects to home
    config.add_route('events_with_slash', '/events/') # redirects to home
    config.add_route('event', '/events/{date}')
    config.add_route('national_event', '/national_events/{year}')
    config.scan()
    return config.make_wsgi_app()
