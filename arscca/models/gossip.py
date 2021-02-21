from plim import preprocessor
import os
import pdb
import re


class Gossip:
    class PlimExtensionError(Exception):
        '''Raised when a gossip file doesn not end in .plim'''

    FILENAME_REGEX = re.compile(r'\A(\w+)\.plim\Z')

    def __init__(self, driver_slug):
        self.driver_slug = driver_slug

    def html(self, expect_presence=False):
        try:
            with open(f'arscca/templates/gossip/{self.driver_slug}.plim', 'r') as gfile:
                text = gfile.read()
                return preprocessor(text)
        except FileNotFoundError as error:
            if expect_presence:
                raise error
            return None

    @classmethod
    def all(cls):
        for filename in os.listdir('arscca/templates/gossip'):
            match = cls.FILENAME_REGEX.match(filename)
            if not match:
                raise cls.PlimExtensionError
            driver_slug = match[1]
            gossip = cls(driver_slug)
            yield gossip


if __name__ == '__main__':
    # Verify that all gossip files render without error
    for gossip in Gossip.all():
        print(gossip.html(True))
