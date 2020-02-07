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
    def test_initialization(self):
        storage = FieldStorageDummy('arscca/test/upload_test_files/xylophone.jpg')
        #import cgi
        #from io import BytesIO
        #fake_stdin = BytesIO(data)
        #store = cgi.FieldStorage(fp=fake_stdin, environ={'content-length':50})

        upload = Upload(storage)
        upload.process()
