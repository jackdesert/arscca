from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name='joomla_test__home_page',
             renderer='templates/joomla_test/home_page.jinja2')
def joomla_test__home_page_view(request):
    return {}
