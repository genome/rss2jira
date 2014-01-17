import feedparser
import logging
import urllib2
import socket

class RssReader(object):
    def __init__(self, feed_url, accept_filter=lambda x: True, timeout=None):
        self.feed_url = feed_url
        self.accept_filter = accept_filter
        self.logger = logging.getLogger("rss2jira")
        self.timeout = timeout
        self.consecutive_failures = 0

    def _fetch_all_entries(self):
        try:
            stream = urllib2.urlopen(self.feed_url, timeout=self.timeout)
            entries = feedparser.parse(stream).entries
            self.consecutive_failures = 0
            return entries
        except Exception as ex:
            self.consecutive_failures += 1
            self.logger.exception("Failed to fetch from url {}".format(
                    self.feed_url))
            raise

    def get_entries(self):
        entries = []
        for e in self._fetch_all_entries():
            if not hasattr(e, 'title') or len(e.title) == 0:
                e.title = 'No Title'

            if self.accept_filter(str(e)):
                entries.append(e)
            else:
                self.logger.debug('Entry does not match keywords, ' +
                    'skipping ({})'.format(e.title.encode('ascii', 'replace')))

        return entries
