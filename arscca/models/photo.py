from arscca.models.canon import Canon
import os
import pdb
import re
import threading

class Photo:
    class SlugError(Exception):
        '''Photo filename_without_ext must not have a .jpg extension'''

    SMALL = 'small'
    MEDIUM = 'medium'

    DIRS = { 'small': '/static/images/driver_photos/small',
             'medium': '/static/images/driver_photos/medium',
           }

    TORSO_SUFFIX_REGEX = re.compile(r'_torso(\.jpg)?$')
    CAR_SUFFIX_REGEX = re.compile(r'_car_?\d*(\.jpg)?$')

    JPEG_SUFFIX = re.compile(r'\.jpg$')

    LOCK = threading.Lock()
    HEAD_SHOTS = {}

    def __init__(self, filename_without_ext):
        # filename_without_ext is expected to be the filename of the photo,
        # without the .jpg extension
        # example: 'haymaker_williams_torso'
        if self.JPEG_SUFFIX.search(filename_without_ext):
            raise self.SlugError
        self.filename_without_ext = filename_without_ext

    def path(self, size, request=None):
        directory = self.DIRS[size]
        output = f'{directory}/{self.filename_without_ext}.jpg'
        if request:
            # Skip first character because it's a forward slash
            base = f'arscca:{output[1:]}'
            output = request.static_path(base)
        return output

    @property
    def driver_name(self):
        name = Canon(self.driver_slug).name
        return name

    @property
    def driver_slug(self):
        dslug = self.filename_without_ext
        dslug = self.TORSO_SUFFIX_REGEX.sub('', dslug)
        dslug = self.CAR_SUFFIX_REGEX.sub('', dslug)
        return dslug

    # This method is here so that we have a callable to sort on
    def _filename_without_ext(self):
        return self.filename_without_ext

    def __repr__(self):
        return f"Photo('{self.filename_without_ext}')"

    @classmethod
    def all_for_driver(cls, driver_slug, test_directory=None):
        directory = test_directory or f'arscca/{cls.DIRS[cls.SMALL]}'
        output = []
        for filename in os.listdir(directory):
            trimmed = cls.TORSO_SUFFIX_REGEX.sub('', filename)
            trimmed = cls.CAR_SUFFIX_REGEX.sub('', trimmed)
            if driver_slug == trimmed:
                filename_without_ext = cls.JPEG_SUFFIX.sub('', filename)
                photo = cls(filename_without_ext)
                output.append(photo)

        return sorted(output, key=cls._filename_without_ext, reverse=True)

    @classmethod
    def all(cls, suffix=TORSO_SUFFIX_REGEX, test_directory=None):
        assert suffix in [cls.TORSO_SUFFIX_REGEX, cls.CAR_SUFFIX_REGEX]
        directory = test_directory or f'arscca/{cls.DIRS[cls.SMALL]}'
        output = []
        for filename in os.listdir(directory):
            if suffix.search(filename):
                filename_without_ext = cls.JPEG_SUFFIX.sub('', filename)
                photo = cls(filename_without_ext)
                output.append(photo)

        return sorted(output, key=cls._filename_without_ext)

    @classmethod
    def slug_and_head_shot(cls, name):
        slug = Canon(name).slug
        head_shot = cls._head_shots_memoized().get(slug)
        if not head_shot:
            return {}
        return dict(slug=slug, head_shot=head_shot)


    @classmethod
    def _head_shots_memoized(cls):
        cls._initialize_head_shots()

        # Not sure if reading cls.HEAD_SHOTS needs to be in a lock or not
        with cls.LOCK:
            return cls.HEAD_SHOTS

    @classmethod
    def _initialize_head_shots(cls):
        # Initializing within a lock so all threads have the same experience
        with cls.LOCK:
            if cls.HEAD_SHOTS:
                return
            for photo in cls.all():
                cls.HEAD_SHOTS[photo.driver_slug] = photo.path(cls.SMALL)


    # __eq__ is defined so we can easily test whether two Photo objects are the same
    def __eq__(self, other):
        if not self.filename_without_ext:
            return False
        return self.filename_without_ext == other.filename_without_ext


if __name__ == '__main__':
    photos = Photo.all()
    one = photos[0]
    one.path('small')
    one.path('medium')
    one.driver_name

    barb = Photo.slug_and_head_shot('Barb Eldredge')
    pdb.set_trace()
    a = 5

