#!/usr/bin/env python

import logging
import sqlite3
import yaml
from rss2jira.source import Source
from rss2jira.issueFactory import IssueFactory
import re
import time


class RSS2JIRA:

    # TODO:
    # - Try-catch connection errors but only tolerate N failures without success?
    # - Shutdown when signal received?

    def __init__(self, conf_path='watcher.conf', reset_db=False):
        self.logger = logging.getLogger('rss2jira')
        self.conf_path = conf_path
        self.expect_conf_path_is_secured()
        self.initialize_from_conf()
        self.initialize_sources_and_issuefactories()
        self.initialize_db(reset_db)

    def expect_conf_path_is_secured(self):
        pass

    def initialize_from_conf(self):
        self.logger.info('Initializing configuration...')
        conf_file = open(self.conf_path)
        self.conf = yaml.load(conf_file)
        conf_file.close()
        self.initialized_from_conf = True

    def initialize_sources_and_issuefactories(self):
        self.logger.info('Initializing sources...')
        self.source_sets = []
        for conf in self.conf['sources']:
            name = conf['name']
            source = Source(conf['feed_url'])
            issueFactory = IssueFactory(
                name=conf['name'],
                url=conf['jira_url'],
                username=conf['jira_username'],
                password=conf['jira_password'],
                projectKey=conf['jira_projectKey'],
                issuetypeName=conf['jira_issuetypeName'],
            )
            self.source_sets.append((name, source, issueFactory))

    def initialize_db(self, reset_db):
        self.logger.info('Initializing DB...')
        self.db = sqlite3.connect(self.conf['db_path'])
        db_cursor = self.db.cursor()
        if reset_db:
            self.logger.info('Reseting DB...')
            db_cursor.execute('DROP TABLE IF EXISTS entries')
        db_cursor.execute('''CREATE TABLE IF NOT EXISTS entries (source_name TEXT, id TEXT, PRIMARY KEY (source_name, id))''')

    def entry_is_tracked(self, source_name, entry):
        db_cursor = self.db.execute("SELECT * FROM entries WHERE source_name = '{}' AND id = '{}'".format(source_name, entry.id))
        rows = db_cursor.fetchall()
        return (False, True)[len(rows) > 0]

    def set_entry_as_tracked(self, source_name, entry):
        self.db.execute("INSERT INTO entries VALUES ('{}', '{}')".format(source_name, entry.id))
        self.db.commit()

    def entry_matches_keywords(self, entry):
        keywords = self.conf['keywords']
        pattern = '|'.join(keywords)
        if hasattr(entry, 'title') and len(entry.title) > 0 and re.match(pattern, entry.title, re.IGNORECASE):
            return True
        if hasattr(entry, 'summary') and len(entry.summary) > 0 and re.match(pattern, entry.summary, re.IGNORECASE):
            return True
        if hasattr(entry, 'content'):
            for content in entry.content:
                if re.match(pattern, content['value'], re.IGNORECASE):
                    return True
        return False

    def loop(self):
        for source_set in self.source_sets:
            source_name, source, issueFactory = source_set[0], source_set[1], source_set[2]
            self.logger.info('Fetching entries for {}.'.format(source_name))
            source.fetch()
            for entry in source.entries:
                if self.entry_is_tracked(source_name, entry):
                    self.logger.debug('Entry is tracked; next entry.')
                    continue
                if not self.entry_matches_keywords(entry):
                    self.logger.debug('Entry does not match keywords; next entry.')
                    continue
                self.logger.debug(entry.title)
                self.logger.debug('Tracking new entry.')
                issueFactory.fromEntry(entry)
                self.set_entry_as_tracked(source_name, entry)

    def main(self, sleep):

        while True:
            self.loop()
            time.sleep(sleep)
