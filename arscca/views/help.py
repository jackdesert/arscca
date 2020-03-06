# Builtin
import pdb

# Third Party
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

# Local
from arscca.models.util import Util





@view_config(route_name='help_index',
             renderer='templates/help_index.jinja2')
def help_index_view(request):
    return {}

@view_config(route_name='help_index_slash')
def help_index_slash_view(request):
    return HTTPFound('/help')

@view_config(route_name='help_show',
             renderer='templates/help_show.jinja2')
def help_scanner_view(request):
    name = request.matchdict.get('document_name')
    filename = f'arscca/templates/help/{name}.md'

    with open(filename, 'r') as ff:
        markdown_string = ff.read()


    # Build context to pass to markdown parser
    ref_page_314 = request.static_url('arscca:static/pdfs/pbt7100-reference-pages-314-316.pdf')
    settings_png = request.static_url('arscca:static/images/axware-barcode-settings.png')
    icons_png = request.static_url('arscca:static/images/axware-barcode-status-icons.png')
    reset_png = request.static_path('arscca:static/images/pbt7100-factory-reset-barcode.png')
    flowchart_svg = request.static_path('arscca:static/images/scanner_flowchart.svg')
    context = dict(ref_page_314=ref_page_314,
                   settings_png=settings_png,
                   reset_png=reset_png,
                   icons_png=icons_png,
                   flowchart_svg=flowchart_svg)

    inner_html = Util.html_from_markdown(markdown_string, context)


    output = dict(inner_html=inner_html,
                  name=name.title())
    return output
