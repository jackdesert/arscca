from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config




@view_config(route_name='help_scanner',
             renderer='templates/help/scanner.jinja2')
def help_scanner_view(request):
    return {}
