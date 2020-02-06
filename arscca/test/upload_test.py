import os
import pdb
import pytest
import shutil
import unittest

from arscca.models.upload import Upload
from arscca.models.upload import SingleImage
from datetime import date

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


