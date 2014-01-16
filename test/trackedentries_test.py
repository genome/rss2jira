#!/usr/bin/env python

import unittest
from tempfile import NamedTemporaryFile
from rss2jira.trackedentries import Sqlite3TrackedEntries

class TestTrackedEntries(unittest.TestCase):
    def setUp(self):
        self.tracked_entries = Sqlite3TrackedEntries(":memory:")

    def test_tracking(self):
        self.assertFalse(self.tracked_entries.contains("a", "b"))
        self.tracked_entries.add("a", "b")
        self.assertTrue(self.tracked_entries.contains("a", "b"))

        self.assertFalse(self.tracked_entries.contains(1, 2))
        self.tracked_entries.add(1, 2)
        self.assertTrue(self.tracked_entries.contains(1, 2))

    def test_clear(self):
        self.tracked_entries.add(1, 2)
        self.assertTrue(self.tracked_entries.contains(1, 2))
        self.tracked_entries.clear()
        self.assertFalse(self.tracked_entries.contains(1, 2))

    def test_commit(self):
        with NamedTemporaryFile() as temp_file:
            db = Sqlite3TrackedEntries(temp_file.name)
            db.add("one", "two")

            # Reopen the same db to see that changes are committed
            db = Sqlite3TrackedEntries(temp_file.name)
            self.assertTrue(db.contains("one", "two"))

            # Make sure clear is persisted
            db.clear()
            db = Sqlite3TrackedEntries(temp_file.name)
            self.assertFalse(db.contains("one", "two"))
