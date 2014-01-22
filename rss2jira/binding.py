import re
import logging
from rssreader import RssReader

class BindingFactory(object):
    def __init__(self, config, tracked_entries, rss_reader_class,
            issue_creator_class):

        self.socket_timeout = config.get("socket_timeout_sec", None)
        self.global_keywords = config.get("keywords", [])
        self.tracked_entries = tracked_entries
        self.rss_reader_class = rss_reader_class
        self.issue_creator_class = issue_creator_class

    def make_filter(self, source_keywords):
        keywords = set(self.global_keywords + source_keywords)
        return re.compile("|".join(keywords), re.IGNORECASE).search

    def create(self, config_entry):
        name = config_entry['name']

        accept_filter = self.make_filter(config_entry.get('keywords', []))
        rss_reader = self.rss_reader_class(
                feed_url=config_entry['feed_url'],
                accept_filter=accept_filter,
                timeout=self.socket_timeout)

        issue_creator = self.issue_creator_class(
                name=config_entry['name'],
                url=config_entry['jira_url'],
                username=config_entry['jira_username'],
                password=config_entry['jira_password'],
                projectKey=config_entry['jira_projectKey'],
                issuetypeName=config_entry['jira_issuetypeName'])

        storage = self.tracked_entries.source_view(name)

        return Binding(name, rss_reader, issue_creator, storage)


class Binding(object):
    def __init__(self, name, rss_reader, issue_creator, tracked_entries):
        self.name = name
        self.rss_reader = rss_reader
        self.issue_creator = issue_creator
        self.tracked_entries = tracked_entries
        self.logger = logging.getLogger('rss2jira')

    def pump(self):
        self.logger.info("Fetching entries from {}".format(self.name))
        try:
            entries = self.rss_reader.get_entries()
        except Exception as ex:
            self.logger.error("{} consecutive failure(s) fetching {}".format(
                    self.rss_reader.consecutive_failures, self.name))
            return

        new_entries = []
        for e in entries:
            if e.id not in self.tracked_entries:
                new_entries.append(e)
            else:
                self.logger.debug('Entry is tracked, skipping. ({})'.format(
                        e.title.encode('ascii', 'replace')))

        self.logger.info("Got {} entries ({} new)".format(len(entries), len(new_entries)))

        for e in new_entries:
            self.issue_creator.create_issue(e)
            self.tracked_entries.add(e.id)
            self.logger.debug('Tracking new entry. ({})'.format(e.title.encode('ascii', 'replace')))
