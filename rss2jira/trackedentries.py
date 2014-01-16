import sqlite3

class _MemoryTrackedEntries(object):
    def __init__(self):
        self.data = set()

    def clear(self):
        self.data.clear()

    def add(self, source_name, identifier):
        self.data.add((source_name, identifier))

    def contains(self, source_name, identifier):
        return (source_name, identifier) in self.data


class Sqlite3TrackedEntries(object):
    _CREATE_ENTRY_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS entries (
        source_name TEXT,
        id TEXT,
        PRIMARY KEY (source_name, id))
    """

    _DROP_ENTRY_TABLE_SQL = "DROP TABLE IF EXISTS entries"

    _ENTRY_EXISTS_SQL = """
    SELECT COUNT(1) FROM entries
    WHERE source_name = '{}' AND id = '{}'
    """

    _INSERT_ENTRY_SQL = "INSERT INTO entries VALUES ('{}', '{}')"

    def __init__(self, db_path):
        self.db_path = db_path
        self.db = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        self.db.cursor().execute(self._CREATE_ENTRY_TABLE_SQL)

    def _drop_tables(self):
        self.db.cursor().execute(self._DROP_ENTRY_TABLE_SQL)

    def clear(self):
        self._drop_tables()
        self._create_tables()

    def contains(self, source_name, identifier):
        sql = self._ENTRY_EXISTS_SQL.format(source_name, identifier)
        result = self.db.cursor().execute(sql)
        return result.fetchone()[0] > 0

    def add(self, source_name, identifier):
        sql = self._INSERT_ENTRY_SQL.format(source_name, identifier)
        self.db.cursor().execute(sql)
        self.db.commit()
