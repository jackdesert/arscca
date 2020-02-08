from PIL import Image
from PIL import UnidentifiedImageError
from uuid import uuid4 # random uuid
import hashlib
import os
import pathlib
import pdb
import re
import shutil
import zipfile


#sudo apt install libpng-dev zlib1g-dev


class SingleImage:

    MEDIUM_SIZE = (600, 600)
    TARGET_DIRECTORY_MEDIUM = '/arscca-pyramid/arscca/static/uploaded'

    def __init__(self, date, filename):
        self._date = date
        self._filename = filename
        self._md5 = None
        self._medium_filename = None

    def process(self):
        self._compute_md5()
        success = self._write_medium()

        if success:
            return self._md5
        else:
            return None

    def _write_medium(self):
        pathlib.Path(self.TARGET_DIRECTORY_MEDIUM).mkdir(exist_ok=True)

        try:
            im = Image.open(self._filename)
        except UnidentifiedImageError:
            return False

        im.thumbnail(self.MEDIUM_SIZE)
        im.save(self._medium_filename, 'PNG')
        im.close()
        return True

    def _compute_md5(self):
        digest = hashlib.md5()
        with open(self._filename, 'rb') as ff:
            digest.update(ff.read())
        md5 = digest.hexdigest()
        self._md5 = md5
        self._medium_filename = f'{self.TARGET_DIRECTORY_MEDIUM}/{self._date}__{md5}.png'




class Upload:
    UPLOADS_DIR = '/tmp/arscca-pyramid-uploads'
    MEDIUM_SIZE = (600, 600)
    DATE_REGEX = re.compile(r'\A\d{4}-\d{2}-\d{2}\Z')

    # field_storage is a cgi.FieldStorage
    def __init__(self, date, field_storage):
        # A field_storage is passed instead of the actual data
        # Hoping to conserve memory
        assert self.DATE_REGEX.match(date)
        self._date = date
        self._field_storage = field_storage
        self._extract_dir = f'{self.UPLOADS_DIR}/{uuid4()}'


    def process(self):
        self._write_to_uploads_dir()
        self._unzip()
        md5s = self._process_images()

        return md5s


    @property
    def _zip_filename(self):
        return f'{self._extract_dir}.zip'


    def _write_to_uploads_dir(self):
        pathlib.Path(self.UPLOADS_DIR).mkdir(exist_ok=True)

        with open(self._zip_filename, 'wb') as writer:
            writer.write(self._field_storage.value)


    def _unzip(self):
        try:
            # If it's a zip file, extract to directory
            with zipfile.ZipFile(self._zip_filename, 'r') as zip_handle:
                zip_handle.extractall(self._extract_dir)
        except zipfile.BadZipFile:
            # Otherwise copy to directory
            pathlib.Path(self._extract_dir).mkdir()
            pathlib.Path(self._zip_filename).rename(f'{self._extract_dir}/image_file')


    def _process_images(self):
        filenames = []

        for path, dirs, files in os.walk(self._extract_dir):
            for local_filename in files:
                filenames.append(f'{path}/{local_filename}')

        md5s = []
        for filename in filenames:
            image = SingleImage(self._date, filename)
            md5 = image.process()
            if md5:
                # md5 will be None for non-image files
                md5s.append(md5)

        self._unlink()

        # Sort these to make tests repeatable
        return sorted(md5s)


    def _unlink(self):
        zipfile_path = pathlib.Path(self._zip_filename)
        if zipfile_path.is_file():
            # Only if the zipfile was actually a zip archive will it still be here
            # (Because if it was a single image, it has already been renamed)
            pathlib.Path(self._zip_filename).unlink()

        # Using shutil.rmtree because we don't know how many levels
        # deep a user will nest their files
        shutil.rmtree(self._extract_dir)



