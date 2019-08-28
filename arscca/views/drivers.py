import pdb
from datetime import date as Date
from pyramid.view import view_config
from arscca.models.gossip import Gossip
from arscca.models.photo import Photo


@view_config(route_name='drivers',
             renderer='templates/drivers.jinja2')
def drivers_view(request):
    photos = Photo.all()
    return dict(photos=photos)

@view_config(route_name='driver',
             renderer='templates/driver.jinja2')
def driver_view(request):
    slug = request.matchdict.get('slug')
    gossip = Gossip(slug)

    name = slug.replace('_', ' ').title()
    photos = Photo.all_for_driver(slug)

    return dict(name=name, photos=photos, gossip=gossip.html())

