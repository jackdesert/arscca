import pdb

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from arscca.models.util import Util


@view_config(route_name='opinion_index',
             renderer='templates/opinion_index.jinja2')
def opinion_index_view(request):
    return {}

@view_config(route_name='opinion_index_slash')
def opinion_index_slash_view(request):
    return HTTPFound('/opinion')

@view_config(route_name='opinion_show',
             renderer='templates/opinion_show.jinja2')
def opinion_show_view(request):
    name = request.matchdict.get('document_name')
    filename = f'arscca/templates/opinion/{name}.md'

    with open(filename, 'r') as ff:
        markdown_string = ff.read()

    inner_html = Util.html_from_markdown(markdown_string)

    output = dict(inner_html=inner_html,
                  name=name.title())
    return output
