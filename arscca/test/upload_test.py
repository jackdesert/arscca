import unittest
import pytest
import pdb


from arscca.models.upload import Upload


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
    def test_initialization_1(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/00_xylophone.jpg')
        upload = Upload(storage)
        md5s = upload.process()
        assert md5s == ['17a04f5d26dc09caf72f2ca90e2a52fa']

    # Zipped, plain
    def test_initialization_2(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/plain.zip')
        upload = Upload(storage)
        md5s = upload.process()
        assert md5s == ['10338522ee0d6ddd72e55efa9d385493',
                        'acd92497072fac99dc82b4748693109a']

    # Zipped, nested
    def test_initialization_3(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/nested.zip')
        upload = Upload(storage)
        md5s = upload.process()
        assert md5s == ['7809413ce19fd04710e8dbdc53798cbd',
                        'e45714b7d004e4dccbb26f6c8626ad5a']



