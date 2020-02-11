from arscca.models.shared import Shared
from arscca.models.upload import SingleImage
from arscca.models.upload import Upload
from arscca.models.util import Util
from collections import defaultdict
from datetime import date as Date
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from threading import Lock
import json
import logging
import pdb
import redis


REDIS = Shared.REDIS
LOG = logging.getLogger(__name__)


@view_config(route_name='photo_upload_new',
             renderer='templates/photo_upload.jinja2')
def photo_upload_new_view(request):
    flash_messages = request.session.pop_flash()
    password_required = not Util.from_arkansas(request)
    return dict(flash_messages=flash_messages,
                password_required=password_required)


# Test with
# curl -XPOST -F "images[]=@/tmp/photos.zip" http://localhost:6543/photos/upload

@view_config(route_name='photo_upload_create',
             renderer='json')
def photo_upload_create_view(request):
    password = request.params.get('password')
    if not Util.user_password_auth(password) and not Util.from_arkansas(request):
        request.session.flash('Password Error or Geolocation Error')
        return HTTPFound(location=request.path)

    storages = request.params.getall('images[]')

    md5s = set()
    ip = request.headers.get('X-Real-Ip')
    for storage in storages:
        if storage == b'':
            # You will arrive here if you do not select a file
            continue
        upload = Upload(storage, ip)
        local_md5s = upload.process()
        for md5 in local_md5s:
            md5s.add(md5)

    if 'curl' in request.user_agent:
        return dict(md5s=list(md5s))
    else:
        # Web requests get redirected
        request.session.flash(f'{len(md5s)} files successfully uploaded. Nice Work!')
        return HTTPFound(location=request.path)



@view_config(route_name='photos',
             renderer='templates/photos.jinja2')
def photos_view(request):
    by_upload_date = bool(request.params.get('g'))
    grouped_keys = SingleImage.redis_keys_grouped_and_sorted(by_upload_date)

    bucket = SingleImage.S3_BUCKET

    return dict(grouped_keys=grouped_keys,
                by_upload_date=by_upload_date,
                bucket=bucket)



