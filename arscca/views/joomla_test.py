from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name='joomla_test__home_page_calendar',
             renderer='templates/joomla_test/home_page_calendar.jinja2')
def joomla_test__home_page_calendar_view(request):
    return {}

@view_config(route_name='joomla_test__home_page_photos',
             renderer='templates/joomla_test/home_page_photos.jinja2')
def joomla_test__home_page_photos_view(request):
    return {}
