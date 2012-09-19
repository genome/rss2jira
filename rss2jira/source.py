import feedparser


class Source:

    def __init__(self, feed_url):
        self.feed_url = feed_url

    def fetch(self):
        self.feed = feedparser.parse(self.feed_url)
        self.entries = []
        self.entries = self.feed.entries
