import feedparser
import logging
import urllib2
import socket

def validate_feed(feed):
    # We're being a bit permissive; so long as the feed got entries we
    # ignore errors. However, if there are no entries AND feedparser's
    # "bozo" bit is set we throw the "bozo_exception".
    # The reason for being lax is that some of the sources we care about
    # generate errors for slightly non-conformant xml.
    if len(feed.entries) == 0 and feed.bozo:
        raise feed.bozo_exception

    return feed


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
            feed = validate_feed(feedparser.parse(stream))
            self.consecutive_failures = 0
            return feed.entries
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
