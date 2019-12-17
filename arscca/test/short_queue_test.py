import unittest
import pytest
import pdb

from arscca.models.short_queue import ShortQueue

from pyramid import testing


class ShortQueueTests(unittest.TestCase):
    # Note these tests do not actually exercise the locking mechanisms in the class
    def test__join(self):
        queue = ShortQueue()
        self.assertEqual(queue.join(), True)
        self.assertEqual(queue.join(), False)
        self.assertEqual(queue.join(), False)
        self.assertEqual(queue.join(), False)

    def test__join_then_leave_then_join(self):
        queue = ShortQueue()
        self.assertEqual(queue.join(), True)
        queue.leave()
        self.assertEqual(queue.join(), True)

    def test__leave(self):
        queue = ShortQueue()
        with pytest.raises(ValueError):
            self.assertEqual(queue.leave(), True)
