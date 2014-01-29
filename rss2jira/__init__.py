__version__ = '0.1.20'

from trackedentries import Sqlite3TrackedEntries
from binding import BindingFactory
from rssreader import RssReader
from app import MainLoop
from issueFactory import JiraWrapper

import logging

try:
    logging.getLogger('rss2jira').addHandler(logging.NullHandler())
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
    logging.getLogger('rss2jira').addHandler(NullHandler())
