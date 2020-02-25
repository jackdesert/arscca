from arscca.models.shared import Shared
from arscca.models.upload import SingleImage
from arscca.models.upload import Upload
from datetime import datetime
from datetime import date
import os
import pdb
import pytest
import shutil
import unittest

def metadata(key):
    today = date.today()
    headers = SingleImage.S3.head_object(Bucket=SingleImage.S3_BUCKET, Key=key)
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
        keys = upload.process()
        assert keys == ['snapped-2008-04-10__0e72357f94407127dd950f3ce4bf8954af6a4842beb2c615d125b837f4946f1b_medium.png']

    # Zipped, plain
    def test_initialization_3(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/plain.zip')
        upload = Upload(storage)
        keys = upload.process()
        today = date.today()
        assert keys == [f'guessed-{today}__17c31999e60f5f6e2282446453e67b26e318f37d14946ed6d3ea5840af6c952b_medium.png',
                        f'guessed-{today}__c559e58035d6e042758a84ea1c1f65d5cf31f10965477d88ee022bb894f904ff_medium.png']

    # Zipped, nested
    def test_initialization_4(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/nested.zip')
        upload = Upload(storage)
        keys = upload.process()
        today = date.today()
        assert keys == [f'guessed-{today}__6175f2cae66964fe925526e129d8af9d96a08be74dc9d00105f16ab0b0ae40c1_medium.png',
                        f'guessed-{today}__ad66e755eb605c03508871673b9efe6e6d1d940931441535f46a6d8cfb873f99_medium.png']


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
        key = upload.process()[0]

        now_truncated = datetime.now().strftime('%Y-%m-%d %H')
        uploaded_at = metadata(key)['uploaded_at']

        # Check enough of the digits that we are confident it is dynamically generated
        assert now_truncated == uploaded_at[0:13]
        assert metadata(key)['ip'] == '192.168.1.1'

    # Verfity No Metadata Set
    def test_initialization_7(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/06_snow__no_meta.jpg')
        upload = Upload(storage)
        key = upload.process()[0]

        assert not 'taken_at' in metadata(key)
        assert not 'ip' in metadata(key)


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
            single._write_key_to_redis(uploaded_at, key)


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
            single._write_key_to_redis(uploaded_at, key)


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
