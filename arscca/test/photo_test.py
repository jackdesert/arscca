from arscca.models.photo import Photo
from pyramid import testing
from random import random
from pathlib import Path
import pdb
import pytest
import unittest

class PhotoTests(unittest.TestCase):
    def test_driver_slug(self):
        photo = Photo('first_last_torso')
        self.assertEqual('first_last', photo.driver_slug)

    def test_driver_slug_2(self):
        photo = Photo('first_last_car')
        self.assertEqual('first_last', photo.driver_slug)


    def test_all(self):
        assert Photo.all()

    def test_head_shots_memoized(self):
        memoized = Photo._head_shots_memoized()
        assert 'adam_cadorette' in memoized

    def test_head_shot(self):
        data = Photo.slug_and_head_shot('Adam. Cadorette')
        assert 'slug' in data
        assert 'head_shot' in data

    def test_head_shot_2(self):
        data = Photo.slug_and_head_shot('Barb Eldredge')
        assert 'slug' in data
        assert 'head_shot' in data

    def test_TORSO_SUFFIX_REGEX(self):
        filenames = { 'barb_eldredge_torso.jpg': '_torso.jpg',
                      'tony_ma.jpg': None }
        for filename, suffix in filenames.items():
            if suffix:
                assert Photo.TORSO_SUFFIX_REGEX.search(filename)[0] == suffix
            else:
                assert not Photo.TORSO_SUFFIX_REGEX.search(filename)
    def test_CAR_SUFFIX_REGEX(self):
        filenames = { 'barb_eldredge_car.jpg'  : '_car.jpg',
                      'barb_eldredge_car1.jpg' : '_car1.jpg',
                      'barb_eldredge_car2.jpg' : '_car2.jpg',
                      'barb_eldredge_car_2.jpg': '_car_2.jpg',
                      'tony_ma.jpg': None }
        for filename, suffix in filenames.items():
            if suffix:
                assert Photo.CAR_SUFFIX_REGEX.search(filename)[0] == suffix
            else:
                assert not Photo.CAR_SUFFIX_REGEX.search(filename)

    def test_all(self):
        directory = f'/tmp/arscca-photos-{random()}'
        Path(directory).mkdir()
        for filename in ['jack_desert_torso.jpg',
                         'jack_prater_torso.jpg',
                         'izabel_santos_torso.jpg']:
            Path(f'{directory}/{filename}').touch()

        photos = Photo.all(test_directory=directory)

        # Note these are in alphabetical order
        assert photos == [Photo('izabel_santos_torso'),
                          Photo('jack_desert_torso'),
                          Photo('jack_prater_torso')]


    def test_all_for_driver(self):
        directory = f'/tmp/arscca-photos-{random()}'
        Path(directory).mkdir()
        for filename in ['jack_desert_torso.jpg',
                         'jack_prater_car.jpg',
                         'izabel_santos_torso.jpg',
                         'sean_philips_torso.jpg',
                         'sean_philips_car.jpg']:
            Path(f'{directory}/{filename}').touch()

        data = { 'jack': 0,
                 'jack_desert': 1,
                 'jack_prater': 1,
                 'izabel_santos': 1,
                 'sean_philips': 2 }
        for slug, count in data.items():
            photos = Photo.all_for_driver(slug, test_directory=directory)
            assert len(photos) == count

