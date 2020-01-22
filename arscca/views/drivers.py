from arscca.models.canon import Canon
from arscca.models.fond_memory import FondMemory
from arscca.models.gossip import Gossip
from arscca.models.photo import Photo
from arscca.models.published_event import PublishedEvent
from datetime import date as Date
from pyramid.view import view_config
import pdb

@view_config(route_name='drivers',
             renderer='templates/drivers.jinja2')
def drivers_view(request):
    photos = Photo.all()
    return dict(photos=photos)

@view_config(route_name='driver',
             renderer='templates/driver.jinja2')
def driver_view(request):
    slug_from_url = request.matchdict.get('slug')
    canon = Canon(slug_from_url)

    slug = canon.slug
    name = canon.name

    gossip = Gossip(slug)
    photos = Photo.all_for_driver(slug)

    event_dates_by_year = PublishedEvent.dates_by_year()

    fond_memories = FondMemory.all_for_driver(slug)

    return dict(name=name,
                photos=photos,
                gossip=gossip.html(),
                event_dates_by_year=event_dates_by_year,
                fond_memories=fond_memories)

