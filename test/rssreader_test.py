from rss2jira.rssreader import RssReader
import tempfile
import os
import re
import unittest
import urllib2
import socket

_FEED_XML = """
<?xml version="1.0" encoding="ISO-8859-1"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Example</title>
    <link>file:///example.xml</link>
    <description>Example description</description>
    <language>en</language>
    <ttl>10</ttl>
    <item>
      <title>title ABC</title>
      <link>file:///example/ABC.xml</link>
      <description>description ABC</description>
      <content:encoded><![CDATA[<div>body ABC</div> ]]></content:encoded>
      <guid isPermaLink="true">file:///example/ABC.xml</guid>
    </item>
    <item>
      <title>title XYZ</title>
      <link>file:///example/XYZ.xml</link>
      <description>description XYZ</description>
      <content:encoded><![CDATA[<div>body XYZ</div> ]]></content:encoded>
      <guid isPermaLink="true">file:///example/XYZ.xml</guid>
    </item>
    <item>
      <link>file:///example/LMN.xml</link>
      <description>description LMN</description>
      <content:encoded><![CDATA[<div>body LMN</div> ]]></content:encoded>
      <guid isPermaLink="true">file:///example/LMN.xml</guid>
    </item>

  </channel>
</rss>
"""

class TestRssReader(unittest.TestCase):
    def setUp(self):
        self.input_file = tempfile.NamedTemporaryFile()
        self.url = "file://{}".format(self.input_file.name)
        self.input_file.write(_FEED_XML)
        self.input_file.flush()

    def test_reader(self):
        reader = RssReader(self.url)
        entries = reader.get_entries()
        self.assertEqual(3, len(entries))

        self.assertEqual("file://example/ABC.xml", entries[0].id)
        self.assertEqual("title ABC", entries[0].title)

        self.assertEqual("file://example/XYZ.xml", entries[1].id)
        self.assertEqual("title XYZ", entries[1].title)

        self.assertEqual("file://example/LMN.xml", entries[2].id)
        self.assertEqual("No Title", entries[2].title)

    def test_filter(self):
        should_match = ["title XYZ", "description XYZ", "body XYZ", "XYZ"]
        for s in should_match:
            match_re = re.compile(s)
            reader = RssReader(self.url, accept_filter=match_re.search)
            entries = reader.get_entries()
            self.assertEqual(1, len(entries))
            self.assertEqual("title XYZ", entries[0].title)

    def test_timeout(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ""
        port = 0 # automatically assign port
        sock.bind((host, port))
        host, port = sock.getsockname() # get actual port
        sock.listen(1)
        reader = RssReader("http://{}:{}/".format(host, port), timeout=0.01)

        self.assertEqual(0, reader.consecutive_failures)
        self.assertSocketTimeout(reader.get_entries)
        self.assertEqual(1, reader.consecutive_failures)
        self.assertSocketTimeout(reader.get_entries)
        self.assertEqual(2, reader.consecutive_failures)

        # point the reader at a valid file to test that consecutive_failures
        # gets reset
        reader.feed_url = self.url
        entries = reader.get_entries()
        self.assertEqual(3, len(entries))
        self.assertEqual(0, reader.consecutive_failures)

        sock.close()

    def test_bad_feed_data(self):
        bad_file = tempfile.NamedTemporaryFile()
        bad_file.write("Ceci n'est pas un flux RSS")
        bad_file.flush()
        url = "file://{}".format(bad_file.name)
        reader = RssReader(url)
        self.assertRaises(Exception, reader.get_entries)

    def assertSocketTimeout(self, callable):
        try:
            callable()
        except socket.timeout as ex:
            return
        except urllib2.URLError as ex:
            if type(ex.reason) == socket.timeout:
                return
            else:
                raise

        raise AssertionError("callable did not raise a socket timeout exception")
