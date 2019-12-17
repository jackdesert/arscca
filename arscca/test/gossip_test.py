import unittest
import pytest
import pdb

from arscca.models.gossip import Gossip
from pyramid import testing
from unittest.mock import patch

class GossipTests(unittest.TestCase):
    def test_html_when_file_not_exist(self):
        gossip = Gossip('unknown_driver_slug')
        with pytest.raises(FileNotFoundError):
            gossip.html(True)

    def test_all(self):
        # Verify that each file renders
        for gossip in Gossip.all():
            gossip.html(True)
