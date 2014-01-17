import logging
import sqlite3

class Sqlite3TrackedEntries(object):
    _CREATE_ENTRY_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS entries (
        source_name TEXT,
        id TEXT,
        PRIMARY KEY (source_name, id))
    """

    _CLEAR_ENTRY_TABLE_SQL = "DELETE FROM entries"

    _ENTRY_EXISTS_SQL = """
    SELECT COUNT(1) FROM entries
    WHERE source_name = '{}' AND id = '{}'
    """

    _INSERT_ENTRY_SQL = "INSERT INTO entries VALUES ('{}', '{}')"

    class _SourceView(object):
        def __init__(self, source_name, tracker):
            self.source_name = source_name
            self.tracker = tracker

        def __contains__(self, x):
            return self.tracker.contains(self.source_name, x)

        def add(self, x):
            self.tracker.add(self.source_name, x)

    def __init__(self, db_path):
        self.logger = logging.getLogger("rss2jira.SQL")
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        self.exec_sql(self._CREATE_ENTRY_TABLE_SQL)
        self.db.commit()

    def clear(self):
        self.exec_sql(self._CLEAR_ENTRY_TABLE_SQL)
        self.db.commit()

    def contains(self, source_name, identifier):
        sql = self._ENTRY_EXISTS_SQL.format(source_name, identifier)
        result = self.exec_sql(sql)
        return result.fetchone()[0] > 0

    def add(self, source_name, identifier):
        sql = self._INSERT_ENTRY_SQL.format(source_name, identifier)
        self.exec_sql(sql)
        self.db.commit()

    def exec_sql(self, sql):
        self.logger.debug(sql)
        return self.db.cursor().execute(sql)

    def source_view(self, source_name):
        return self._SourceView(source_name, self)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.db.close()
