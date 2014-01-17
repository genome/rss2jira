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
            with Sqlite3TrackedEntries(temp_file.name) as db:
                db.add("one", "two")

            # Reopen the same db to see that changes are committed
            with Sqlite3TrackedEntries(temp_file.name) as db:
                db = Sqlite3TrackedEntries(temp_file.name)
                self.assertTrue(db.contains("one", "two"))

                # Make sure clear is persisted
                db.clear()

            with Sqlite3TrackedEntries(temp_file.name) as db:
                db = Sqlite3TrackedEntries(temp_file.name)
                self.assertFalse(db.contains("one", "two"))

    def test_source_entries(self):
        view_a = self.tracked_entries.source_view("source a")
        view_b = self.tracked_entries.source_view("source b")

        view_a.add(1)
        self.assertTrue(1 in view_a)

        view_b.add(2)
        self.assertTrue(2 in view_b)

        self.assertFalse(2 in view_a)
        self.assertFalse(1 in view_b)
