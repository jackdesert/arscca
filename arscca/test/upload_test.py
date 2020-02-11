from arscca.models.shared import Shared
from arscca.models.upload import SingleImage
from arscca.models.upload import Upload
from datetime import date
import os
import pdb
import pytest
import shutil
import unittest

def metadata(md5):
    today = date.today()
    headers = SingleImage.S3.head_object(Bucket=SingleImage.S3_BUCKET,
                                         Key=f'{today}__{md5}_medium.png')
    return headers['Metadata']

# This dummy only needs to respond to the "value" method
# And that way we don't have to figure out how to populate an cgi.FieldStorage object
class FieldStorageDummy:
    def __init__(self, filename):
        with open(filename, 'rb') as ff:
            self._value = ff.read()

    @property
    def value(self):
        return self._value


class UploadTests(unittest.TestCase):

    # Not Zipped
    def test_initialization_2(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/00_xyl__with_meta.jpg')
        upload = Upload(storage)
        md5s = upload.process()
        assert md5s == ['17a04f5d26dc09caf72f2ca90e2a52fa']

    # Zipped, plain
    def test_initialization_3(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/plain.zip')
        upload = Upload(storage)
        md5s = upload.process()
        assert md5s == ['10338522ee0d6ddd72e55efa9d385493',
                        'acd92497072fac99dc82b4748693109a']

    # Zipped, nested
    def test_initialization_4(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/nested.zip')
        upload = Upload(storage)
        md5s = upload.process()
        assert md5s == ['7809413ce19fd04710e8dbdc53798cbd',
                        'e45714b7d004e4dccbb26f6c8626ad5a']

    # Verify No Temp Files Remain
    def test_initialization_5(self):
        # Clear out any preexisting files
        shutil.rmtree(Upload.UPLOADS_DIR)
        storage = FieldStorageDummy('arscca/test/upload_test_files/nested.zip')
        upload = Upload(storage)
        upload.process()
        assert os.listdir(Upload.UPLOADS_DIR) == []

    # Verify Metadata Set
    def test_initialization_6(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/00_xyl__with_meta.jpg')
        upload = Upload(storage, '192.168.1.1')
        md5 = upload.process()[0]

        assert metadata(md5)['taken_at'] == '2008:04:10 15:34:54'
        assert metadata(md5)['ip'] == '192.168.1.1'

    # Verfity No Metadata Set
    def test_initialization_7(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/06_snow__no_meta.jpg')
        upload = Upload(storage)
        md5 = upload.process()[0]

        assert not 'taken_at' in metadata(md5)
        assert not 'ip' in metadata(md5)


    # Default grouping/sorting
    def test_redis_keys_grouped_and_sorted_1(self):
        # Specify alternate REDIS database
        import redis
        Shared.REDIS = redis.StrictRedis(host='arscca-redis', port=6379, db=14, decode_responses=True)
        Shared.REDIS.flushdb()

        # This data is ordered by snap_date, then by uploaded_at
        data = [('snapped-2010-01-01__blah6', '2012-03-01 12:00:00'),
                ('snapped-2010-01-01__blah5', '2012-03-01 12:01:00'),
                ('snapped-2010-01-02__blah4', '2012-02-02 12:00:00'),
                ('snapped-2010-01-02__blah3', '2012-02-02 12:03:00'),
                ('snapped-2010-01-03__blah2', '2012-01-02 12:02:00'),
                ('snapped-2010-01-03__blah1', '2012-01-02 12:05:00')]

        single = SingleImage(None, None)
        for key, uploaded_at in data:
            single._write_key_to_redis(key, uploaded_at)


        # THIS LINE IS DIFFERENT
        # default group/sort
        groups = SingleImage.redis_keys_grouped_and_sorted()
        expected = [
                    ('2010-01-03',
                     'January  3, 2010',
                     ['snapped-2010-01-03__blah1', 'snapped-2010-01-03__blah2']),
                    ('2010-01-02',
                     'January  2, 2010',
                     ['snapped-2010-01-02__blah3', 'snapped-2010-01-02__blah4']),
                    ('2010-01-01',
                     'January  1, 2010',
                     ['snapped-2010-01-01__blah5', 'snapped-2010-01-01__blah6']),
                   ]

        assert groups == expected

    # Group/sort by uploaded_at
    def test_redis_keys_grouped_and_sorted_2(self):
        # Specify alternate REDIS database
        import redis
        Shared.REDIS = redis.StrictRedis(host='arscca-redis', port=6379, db=14, decode_responses=True)
        Shared.REDIS.flushdb()

        # This data is ordered by uploaded_at
        data = [ # snap_date         # md5   # uploaded_at
                ('snapped-2010-01-03__blah2', '2012-01-01 12:00:00'),
                ('snapped-2010-01-02__blah4', '2012-01-01 12:01:00'),

                ('snapped-2010-01-02__blah3', '2012-02-01 12:00:00'),
                ('snapped-2010-01-03__blah1', '2012-02-01 12:01:00'),

                ('snapped-2010-01-01__blah6', '2012-03-01 12:00:00'),
                ('snapped-2010-01-01__blah5', '2012-03-01 12:01:00'),
               ]

        single = SingleImage(None, None)
        for key, uploaded_at in data:
            single._write_key_to_redis(key, uploaded_at)


        # THIS LINE IS DIFFERENT
        # group/sort by uploaded_at (note True argument to method)
        groups = SingleImage.redis_keys_grouped_and_sorted(True)
        expected = [
                    ('2012-03-01',
                     'March  1, 2012',
                     ['snapped-2010-01-01__blah5', 'snapped-2010-01-01__blah6']),
                    ('2012-02-01',
                     'February  1, 2012',
                     ['snapped-2010-01-03__blah1', 'snapped-2010-01-02__blah3']),
                    ('2012-01-01',
                     'January  1, 2012',
                     ['snapped-2010-01-02__blah4', 'snapped-2010-01-03__blah2']),
                   ]

        assert groups == expected
