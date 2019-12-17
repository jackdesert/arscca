import unittest
import pytest
import pdb

from arscca.models.canon import Canon

class CanonTests(unittest.TestCase):
    def test_slug(self):
        data = {'Hi There'    : 'hi_there',
                ' Bona Fide ' : 'bona_fide',
                'Mr. Robinson': 'mr_robinson',
                'mr_tee'      : 'mr_tee'}

        for name_or_slug, expected_slug in data.items():
            slug = Canon(name_or_slug).slug
            self.assertEqual(slug, expected_slug)

    def test_name(self):
        data = {'Hi There'    : 'Hi There',
                ' Bona Fide ' : 'Bona Fide',
                'Mr. Robinson': 'Mr Robinson',
                'mr_tee'      : 'Mr Tee'}

        for name_or_slug, expected_name in data.items():
            slug = Canon(name_or_slug).name
            self.assertEqual(slug, expected_name)
