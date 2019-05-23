import os
import pdb
import re
import threading

class Photo:
    class SlugError(Exception):
        '''Photo slug must not have a .jpg extension'''

    SMALL = 'small'
    MEDIUM = 'medium'

    DIRS = { 'small': '/static/images/driver_photos/small',
             'medium': '/static/images/driver_photos/medium',
           }

    UNDERSCORE = '_'
    SPACE = ' '

    TORSO_SUFFIX = re.compile(r'_torso(\.jpg)?$')
    CAR_SUFFIX = re.compile(r'_car(\.jpg)?$')

    JPEG_SUFFIX = re.compile(r'\.jpg$')

    LOCK = threading.Lock()
    HEAD_SHOTS = {}

    NON_WORD_CHARS = re.compile(r'[^\w]+')
    WHITESPACE_CHARS = re.compile(r'\s+')

    # { website_slug : photo_slug }
    ALIASES = {'joshua_mapili': 'josh_mapili',
               'nicholas_mellenthin': 'nick_mellenthin',
               'richard_davis': 'rick_davis',
               'kenneth_hiegel': 'kenny_hiegel',
               'james_express_lane': 'james_lane',
               'philip_rucker': 'phil_rucker',
               'alexander_ross': 'alex_ross',
               'jeff_gibson': 'jeff_gilson'}


    def __init__(self, slug):
        # slug is expected to be the filename of the photo,
        # without the .jpg extension
        # example: 'haymaker_williams_torso'
        if self.JPEG_SUFFIX.search(slug):
            raise self.SlugError
        self.slug = slug

    def path(self, size, request=None):
        directory = self.DIRS[size]
        output = f'{directory}/{self.slug}.jpg'
        if request:
            # Skip first character because it's a forward slash
            base = f'arscca:{output[1:]}'
            output = request.static_path(base)
        return output

    @property
    def driver_name(self):
        name = self.driver_slug.replace(self.UNDERSCORE, self.SPACE).title()
        return name

    @property
    def driver_slug(self):
        dslug = self.slug
        dslug = self.TORSO_SUFFIX.sub('', dslug)
        dslug = self.CAR_SUFFIX.sub('', dslug)
        return dslug

    # This method is here so that we have a callable to sort on
    def _slug(self):
        return self.slug

    def __repr__(self):
        return f"Photo('{self.slug}')"

    @classmethod
    def all_for_driver(cls, driver_slug):
        directory = f'arscca/{cls.DIRS[cls.SMALL]}'
        output = []
        for name in os.listdir(directory):
            if name.startswith(driver_slug):
                slug = cls.JPEG_SUFFIX.sub('', name)
                photo = cls(slug)
                output.append(photo)

        return sorted(output, key=cls._slug, reverse=True)

    @classmethod
    def all(cls, suffix=TORSO_SUFFIX):
        assert suffix in [cls.TORSO_SUFFIX, cls.CAR_SUFFIX]
        directory = f'arscca/{cls.DIRS[cls.SMALL]}'
        output = []
        for name in os.listdir(directory):
            if suffix.search(name):
                slug = cls.JPEG_SUFFIX.sub('', name)
                photo = cls(slug)
                output.append(photo)

        return sorted(output, key=cls._slug)

    @classmethod
    def slug_and_head_shot(cls, name):
        slug = cls.WHITESPACE_CHARS.sub(cls.UNDERSCORE, name)
        slug = cls.NON_WORD_CHARS.sub('', slug)
        slug = slug.lower()
        canonical_slug = cls.ALIASES.get(slug) or slug
        head_shot = cls._head_shots_memoized().get(canonical_slug)
        if not head_shot:
            return {}
        return dict(slug=canonical_slug, head_shot=head_shot)


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




if __name__ == '__main__':
    photos = Photo.all()
    one = photos[0]
    one.path('small')
    one.path('medium')
    one.driver_name

    barb = Photo.slug_and_head_shot('Barb Eldredge')
    pdb.set_trace()
    a = 5

