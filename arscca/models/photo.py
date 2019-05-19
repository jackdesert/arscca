import os
import pdb

class Photo:
    SMALL = 'small'
    MEDIUM = 'medium'

    DIRS = { 'small': '/static/images/driver_photos/small',
             'medium': '/static/images/driver_photos/medium',
           }

    UNDERSCORE = '_'
    SPACE = ' '

    TORSO = '_torso'
    CAR = '_car'

    SUFFIX = '.jpg'

    def __init__(self, slug):
        self.slug = slug

    def path(self, size):
        directory = self.DIRS[size]
        return f'{directory}/{self.slug}.jpg'

    @property
    def driver_name(self):
        return self.slug.replace(self.TORSO, ''). \
                         replace(self.CAR, ''). \
                         replace(self.UNDERSCORE, self.SPACE). \
                         title()

    # This method is here so that we have a callable to sort on
    def _slug(self):
        return self.slug

    def __repr__(self):
        return f"Photo('{self.slug}')"

    @classmethod
    def all(cls, size=MEDIUM, focus=TORSO):
        assert focus in [cls.TORSO, cls.CAR]
        directory = f'arscca/{cls.DIRS[size]}'
        output = []
        for name in os.listdir(directory):
            if focus in name:
                name_trimmed =name.replace(cls.SUFFIX, '')
                photo = cls(name_trimmed)
                output.append(photo)

        return sorted(output, key=cls._slug)


if __name__ == '__main__':
    photos = Photo.all()
    one = photos[0]
    one.path('small')
    one.path('medium')
    one.driver_name
    pdb.set_trace()
    a = 5

