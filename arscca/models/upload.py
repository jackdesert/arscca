from PIL import Image
from PIL import ExifTags
from PIL import UnidentifiedImageError
from arscca.models.shared import Shared
from collections import defaultdict
from datetime import datetime
from datetime import date
from uuid import uuid4  # random uuid
import boto3
import hashlib
import json
import os
import pathlib
import pdb
import re
import shutil
import zipfile


# sudo apt install libpng-dev zlib1g-dev


class SingleImage:

    EXTENSION_ORIGINAL = '.png'
    EXTENSION_MEDIUM = '_medium.png'

    MEDIUM_SIZE = (600, 600)

    EXIF_DATETIME_ORIGINAL_KEY = 36867

    COLON = ':'
    HYPHEN = '-'
    SPLITTER = '__'

    # PUBLIC_READ makes it so the uploaded file is readable by anyone
    PUBLIC_READ = 'public-read'

    with open('config/aws_credentials.json', 'r') as ff:
        __CREDS = json.loads(ff.read())

    S3 = boto3.client(
        's3',
        aws_access_key_id=__CREDS['access_key_id'],
        aws_secret_access_key=__CREDS['secret_access_key'],
    )
    S3_BUCKET = __CREDS['s3_bucket']

    def __init__(self, filename, ip):
        self._filename = filename
        self._ip = ip
        self._md5 = None
        self._s3_key_medium = None

    def process(self):
        self._compute_md5()
        success = self._write_medium()

        if success:
            return self._s3_key_medium
        else:
            return None

    def _write_medium(self):
        try:
            im = Image.open(self._filename)
        except UnidentifiedImageError:
            print(f'  ERROR {self._filename}')
            return False

        # Source: ??
        # exif = { ExifTags.TAGS[k]: v for k, v in im._getexif().items() if k in ExifTags.TAGS }   # taken_at = exif['DateTime']
        if snap_timestamp := im.getexif().get(self.EXIF_DATETIME_ORIGINAL_KEY):
            snap_date = snap_timestamp[0:10].replace(self.COLON, self.HYPHEN)
            snapped = True
        else:
            snap_date = date.today()
            snapped = False

        self._compute_s3_key_medium(snap_date, snapped)

        # boto3 encodes all metadata values to ASCII
        # Therefore do not included metadata if it has None values in it
        # Because None.encode() raises an error
        extra_args = dict(ACL=self.PUBLIC_READ)

        uploaded_at = str(datetime.now())
        metadata = dict(uploaded_at=uploaded_at)

        if ip := self._ip:
            metadata.update(ip=ip)

        extra_args.update(Metadata=metadata)

        im.thumbnail(self.MEDIUM_SIZE)
        im.save(self._medium_temp_filename, 'PNG')
        im.close()

        print(f'Uploading {self._filename} as {self._md5}')
        self.S3.upload_file(
            self._filename, self.S3_BUCKET, self._s3_key_medium, ExtraArgs=extra_args
        )

        self._write_key_to_redis(uploaded_at)

        self._unlink(self._medium_temp_filename)

        return True

    def _compute_s3_key_medium(self, snap_date, snapped):
        # Ideally we have the snap date from exif metadata (snapped)
        # Otherwise, we used the prepend "guessed" to differentiate
        prepend = 'snapped' if snapped else 'guessed'
        self._s3_key_medium = (
            f'{prepend}-{snap_date}{self.SPLITTER}{self._md5}{self.EXTENSION_MEDIUM}'
        )

    # test_key is only passed in during automated tests
    def _write_key_to_redis(self, uploaded_at, test_key=None):
        key = test_key or self._s3_key_medium
        Shared.REDIS.hset(Shared.REDIS_KEY_S3_PHOTOS, key, uploaded_at)

    def _compute_md5(self):
        digest = hashlib.sha256()
        with open(self._filename, 'rb') as ff:
            digest.update(ff.read())
        md5 = digest.hexdigest()
        self._md5 = md5

    def _unlink(self, filename):
        pathlib.Path(filename).unlink()

    @property
    def _medium_temp_filename(self):
        return self._filename.replace(self.EXTENSION_ORIGINAL, self.EXTENSION_MEDIUM)

    @classmethod
    def redis_keys_grouped_and_sorted(cls, group_and_sort_by_upload_date=False):
        """Retuns S3 photo keys grouped by date
        Sample Output:

        [
            ('2018-02-05', 'Feb 5, 2018', ['key-6', 'key-5', 'key-4']),
            ('2018-02-04', 'Feb 4, 2018', ['key-3', 'key-2', 'key-1']),
        ]
        """

        cursor = 0
        data = []
        while True:
            cursor, items = Shared.REDIS.hscan(Shared.REDIS_KEY_S3_PHOTOS, cursor)
            for key_with_snap_date_and_md5, upload_timestamp in items.items():
                if group_and_sort_by_upload_date:
                    sort_string = upload_timestamp
                    date_to_group_by = sort_string[0:10]
                else:
                    #
                    a = key_with_snap_date_and_md5.split(cls.SPLITTER)[0]
                    sort_string = f'{a} {upload_timestamp}'
                    date_to_group_by = a[8:18]
                data.append((sort_string, date_to_group_by, key_with_snap_date_and_md5))

            if cursor == 0:
                break

        output_dict = defaultdict(list)

        # Data will be sorted by first item (sort string),
        # which will set how things are ordered within a group
        for ss, date, key in sorted(data, reverse=True):
            output_dict[date].append(key)

        output_list = sorted(output_dict.items(), reverse=True)

        output = []

        for date, keys in output_list:
            friendly_date = datetime.strptime(date, '%Y-%m-%d').strftime('%B %e, %Y')
            output.append((date, friendly_date, keys))

        return output


class Upload:
    UPLOADS_DIR = '/tmp/arscca-pyramid-uploads'
    MEDIUM_SIZE = (600, 600)
    DATE_REGEX = re.compile(r'\A\d{4}-\d{2}-\d{2}\Z')

    # field_storage is a cgi.FieldStorage
    def __init__(self, field_storage, ip=None):
        # A field_storage is passed instead of the actual data
        # Hoping to conserve memory
        self._field_storage = field_storage
        self._ip = ip
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
            image = SingleImage(filename, self._ip)
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


if __name__ == '__main__':
    print(SingleImage.redis_keys_grouped_and_sorted())
