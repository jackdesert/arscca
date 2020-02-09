import json
import logging
import pdb
import redis

from arscca.models.shared import Shared
from arscca.models.upload import Upload
from arscca.models.util import Util
from datetime import date as Date
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from threading import Lock


REDIS = Shared.REDIS
LOG = logging.getLogger(__name__)


@view_config(route_name='photo_upload_new',
             renderer='templates/photo_upload.jinja2')
def photo_upload_new_view(request):
    date = request.matchdict['date']
    flash_messages = request.session.pop_flash()
    if not Util.from_arkansas(request):
        flash_messages = ['Geolocation Error']
    return dict(date=date, flash_messages=flash_messages)


# Test with
#  curl -XPOST -F "images[]=@./xyl.jpg" http://localhost:6543/events/2019-12-10/upload

@view_config(route_name='photo_upload_create',
             renderer='json')
def photo_upload_create_view(request):
    if not Util.from_arkansas(request):
        return dict(error='Geolocation Error')

    date = request.matchdict['date']
    storages = request.params.getall('images[]')

    md5s = set()
    for storage in storages:
        upload = Upload(date, storage)
        local_md5s = upload.process()
        for md5 in local_md5s:
            md5s.add(md5)

    if 'curl' in request.user_agent:
        return dict(md5s=list(md5s))
    else:
        # Web requests get redirected
        request.session.flash(f'{len(md5s)} files successfully uploaded. Nice Work!')
        return HTTPFound(location=request.path)



@view_config(route_name='event_photos',
             renderer='templates/event_photos.jinja2')
def event_photos_view(request):
    keys = REDIS.smembers(Shared.REDIS_KEY_S3_PHOTOS)
    return dict(keys=keys)



