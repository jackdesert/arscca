from arscca.models.calendar.presenter import Presenter
from arscca.models.shared import Shared
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import logging
import pdb


LOG = logging.getLogger('arscca')


@view_config(route_name='calendar',
             renderer='templates/calendar.jinja2')
def calendar_view(request):
    return _context()

@view_config(route_name='calendar_slash')
def calendar_slash_view(request):
    return HTTPFound('/calendar')


@view_config(route_name='calendar_plain',
             renderer='templates/calendar_plain.jinja2')
def calendar_plain_view(request):
    origin = request.headers.get('Origin')
    if origin in Shared.CORS_DOMAINS:
        # Set CORS headers for cross-domain usage because arscca.org displays this content
        request.response.headers['Access-Control-Allow-Origin'] = origin

    short = bool(request.params.get('short'))
    return _context(short)


def _context(short=False):
    presenter = Presenter(short)
    events = presenter.sorted_future_events()


    return dict(events=events, short=short)
