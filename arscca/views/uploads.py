import json
import logging
import pdb
import redis

from arscca.models.shared import Shared
from arscca.models.upload import Upload
from datetime import date as Date
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from threading import Lock


REDIS = Shared.REDIS
LOG = logging.getLogger(__name__)

# Test with
#  curl -XPOST -F "file=@./xyl.jpg" http://localhost:6543/events/2019-12-10/upload

@view_config(route_name='photo_upload',
             renderer='json')
def photo_upload_view(request):
    storage = request.params.get('file')
    upload = Upload(storage)
    md5s = upload.process()
    return dict(md5s=md5s)

