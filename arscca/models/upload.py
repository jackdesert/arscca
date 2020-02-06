import pdb
import hashlib
import pathlib
from PIL import Image


#sudo apt install libpng-dev zlib1g-dev

class Upload:
    TEMP_DIR_BASE = '/tmp/arscca-pyramid-uploads'
    MEDIUM_SIZE = (600, 600)

    def __init__(self, request):
        # A request is passed instead of a blob
        # so we don't have to create a blob and still have the request
        # (Hoping to save memory)
        self._request = request
        self._tempdir = None
        self._md5 = None

    def process(self):
        self._write_original_to_disk()
        self._write_medium_to_disk()
        return [self._md5]

    def _write_original_to_disk(self):
        cgi_fieldstorage = self._request.params.get('file')
        digest = hashlib.md5()
        digest.update(cgi_fieldstorage.value)
        self._md5 = digest.hexdigest()
        self._create_temp_dir()
        with open(self._original_path, 'wb') as writer:
            writer.write(cgi_fieldstorage.value)

    def _write_medium_to_disk(self):
        with Image.open(self._original_path) as im:
            im.thumbnail(self.MEDIUM_SIZE)
            im.save(self._medium_path, 'PNG')


    def _create_temp_dir(self):
        pathlib.Path(self._temp_dir).mkdir(parents=True, exist_ok=True)

    @property
    def _temp_dir(self):
        if not self._md5:
            raise '_md5 is falsy'

        return f'{self.TEMP_DIR_BASE}/{self._md5}'

    @property
    def _original_path(self):
        return f'{self._temp_dir}/original'

    @property
    def _medium_path(self):
        return f'{self._temp_dir}/medium.png'
