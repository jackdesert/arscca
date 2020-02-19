from arscca.models.calendar.presenter import Presenter
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import logging
import pdb


LOG = logging.getLogger(__name__)

CORS_DOMAINS = frozenset(['http://arscca.org'])


@view_config(route_name='calendar',
             renderer='templates/calendar.jinja2')
def calendar_view(request):
    return _context()


@view_config(route_name='calendar_plain',
             renderer='templates/calendar_plain.jinja2')
def calendar_plain_view(request):
    origin = request.headers.get('Origin')
    if origin in CORS_DOMAINS:
        # Set CORS headers for cross-domain usage
        request.response.headers['Access-Control-Allow-Origin'] = origin

    short = bool(request.params.get('short'))
    return _context(short)


def _context(short=False):
    presenter = Presenter(short)
    events = presenter.sorted_future_events()


    return dict(events=events, short=short)
