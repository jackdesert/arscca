from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config




@view_config(route_name='documentation_scanner',
             renderer='templates/scanner.jinja2')
def documentation_scanner_view(request):
    return {}
