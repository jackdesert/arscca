import json
import pdb
from pyramid.view import view_config
from .models.driver import Driver
from .models.parser import Parser

@view_config(route_name='home',
             renderer='json') #renderer='templates/mytemplate.jinja2')
def my_view(request):
    url = 'http://arscca.org/index.php?option=com_content&view=article&id=398:2018-solo-ii-event-6-final&catid=125&Itemid=103'

    parser = Parser(url)
    parser.parse()
    parser.rank_drivers()
    dict_drivers = [driver.__dict__ for driver in parser.drivers]


    return dict(drivers=dict_drivers)
