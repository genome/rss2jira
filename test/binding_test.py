from rss2jira.binding import Binding, BindingFactory
from rss2jira.trackedentries import Sqlite3TrackedEntries
from rss2jira.rssreader import RssReader

import re
import mock
import unittest
from testhelpers import RegexMatcher

def _make_entry(title):
    entry = mock.Mock()
    title = str(title)
    entry.id = title
    entry.title = title
    entry.description = title
    return entry

def _make_config_source(n, extra_keywords=None):
    rv = {"name": "src{}".format(n),
            "feed_url": "http://feed_url{}".format(n),
            "jira_url": "https://jira_url{}".format(n),
            "jira_username": "jira_user{}".format(n),
            "jira_password": "jira_pass{}".format(n),
            "jira_projectKey": "jira_proj{}".format(n),
            "jira_issuetypeName": "jira_type{}".format(n)}

    if extra_keywords is not None:
        rv["keywords"] = extra_keywords

    return rv

def mock_issue_creator(*args, **kwargs):
    rv = mock.Mock()
    rv(*args, **kwargs)
    return rv


class TestBindingFactory(unittest.TestCase):
    def setUp(self):
        self.config = {
                "keywords": ["cat", "pig", "frog"],
                "socket_timeout_sec": 20,
                "db_path": ":memory:",
                "sources": [
                    _make_config_source(1, ["kw1"]),
                    _make_config_source(2, ["kw2"]),
                    ],
                }

        self.tracked_entries = Sqlite3TrackedEntries(":memory:")
        self.factory = BindingFactory(self.config, self.tracked_entries,
                rss_reader_class=RssReader,
                issue_creator_class=mock_issue_creator)

    def test_create(self):
        bindings = [self.factory.create(x) for x in self.config['sources']]
        self.assertEqual(2, len(bindings))

        self.assertEqual("http://feed_url1", bindings[0].rss_reader.feed_url)
        self.assertEqual(20, bindings[0].rss_reader.timeout)
        self.assertTrue(bindings[0].rss_reader.accept_filter("cat"))
        self.assertTrue(bindings[0].rss_reader.accept_filter("pig"))
        self.assertTrue(bindings[0].rss_reader.accept_filter("frog"))
        self.assertTrue(bindings[0].rss_reader.accept_filter("kw1"))
        self.assertFalse(bindings[0].rss_reader.accept_filter("kw2"))

        self.assertEqual("http://feed_url2", bindings[1].rss_reader.feed_url)
        self.assertEqual(20, bindings[1].rss_reader.timeout)
        self.assertTrue(bindings[1].rss_reader.accept_filter("cat"))
        self.assertTrue(bindings[1].rss_reader.accept_filter("pig"))
        self.assertTrue(bindings[1].rss_reader.accept_filter("frog"))
        self.assertTrue(bindings[1].rss_reader.accept_filter("kw2"))
        self.assertFalse(bindings[1].rss_reader.accept_filter("kw1"))

        bindings[0].issue_creator.assert_called_once_with(
                username="jira_user1",
                name="src1",
                url="https://jira_url1",
                password="jira_pass1",
                projectKey="jira_proj1",
                issuetypeName="jira_type1")

        bindings[1].issue_creator.assert_called_once_with(
                username="jira_user2",
                name="src2",
                url="https://jira_url2",
                password="jira_pass2",
                projectKey="jira_proj2",
                issuetypeName="jira_type2")


class TestBinding(unittest.TestCase):
    def setUp(self):
        self.name = "test_feed"
        self.tracked_entries = Sqlite3TrackedEntries(":memory:")
        self.reader = mock.Mock()
        self.entries = [_make_entry(x) for x in xrange(5)]
        self.reader.get_entries = mock.Mock(return_value=self.entries)
        self.issue_creator = mock.Mock()
        self.binding = Binding(self.name, self.reader, self.issue_creator,
                self.tracked_entries.source_view(self.name))

    def test_pump(self):
        # Make sure new issues get created
        self.binding.pump()
        expected_calls = [mock.call(x) for x in self.entries]
        self.issue_creator.create_issue.assert_has_calls(expected_calls)

        self.issue_creator.create_issue.reset_mock()

        # Make sure they don't get created again
        self.binding.pump()
        self.assertFalse(self.issue_creator.create_issue.called)

        # Clear the database and see that now the issues will be recreated
        self.tracked_entries.clear()
        self.binding.pump()
        self.issue_creator.create_issue.assert_has_calls(expected_calls)

    def test_reader_exception_logging(self):
        self.binding.logger.error = mock.Mock()
        self.reader.consecutive_failures = 1
        self.reader.get_entries.side_effect = RuntimeError("boom")
        self.binding.pump()
        expected_matcher = RegexMatcher("1 consecutive fail")
        self.binding.logger.error.assert_called_once_with(expected_matcher)
