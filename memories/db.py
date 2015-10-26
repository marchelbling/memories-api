import os
import sqlite3
from ConfigParser import RawConfigParser


def safe_utf8(string):
    def safe_decode(string):
        try:
            return unicode(string, 'utf8')
        except UnicodeError:
            try:
                return unicode(string, 'latin1')
            except UnicodeError:
                return unicode(string, 'utf8', 'replace')

    if string is None:
        return string

    if not isinstance(string, unicode):
        string = safe_decode(string)
    return string.encode('utf8')


class ConfigManager:
    config = RawConfigParser()
    config.read("config.rc")
    sql_types = {"title":       "TEXT",
                 "year":        "INTEGER",
                 "country":     "TEXT",
                 "url":         "TEXT",
                 "description": "TEXT"}

    @staticmethod
    def get(*attr):
        return ConfigManager.config.get(*attr)

    @staticmethod
    def sql_type(column):
        return ConfigManager.sql_types.get(column, None)


class MemoriesDB(object):
    db = os.path.join(ConfigManager.get("memories", "storage"),
                      ConfigManager.get("memories", "db_name"))

    @staticmethod
    def get_connection():
        def dict_factory(cursor, row):
            result = {}
            for idx, column in enumerate(cursor.description):
                result[column[0]] = row[idx]
            return result

        connection = sqlite3.connect(MemoriesDB.db, isolation_level=None)
        connection.row_factory = dict_factory  # retrieve row as dict
        connection.text_factory = lambda string: unicode(string, "utf-8", errors="ignore")
        return connection


class MemoriesTable(object):
    def __init__(self, table_name, schema, unicity=None):
        self.table_name = table_name
        self.schema = schema
        self.unicity = unicity
        self.connection = MemoriesDB.get_connection()

    def table_schema(self):
        return ", ".join(["{c} {t}".format(c=column, t=type) for column, type in self.schema] +
                         ["UNIQUE({}) ON CONFLICT REPLACE".format(", ".join(self.unicity))] if self.unicity else [])

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA cache_size = 20000;")
        cursor.execute("PRAGMA page_size = 4096;")
        cursor.execute("PRAGMA temp_store = MEMORY;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA locking_mode = NORMAL;")
        cursor.execute("CREATE TABLE IF NOT EXISTS {} ({})"
                       .format(self.table_name, self.table_schema()))

    def drop_table(self):
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS {table}".format(table=self.table_name))

    def index_name(self, column):
        return "mmr_{table}_{column}".format(table=self.table_name, column=column)

    def create_index(self, column):
        if self.index_column:
            cursor = self.connection.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS {column}_idx ON {table} ({column} ASC)"
                           .format(column=self.index_name(column),
                                   table=self.table_name))

    def drop_index(self, column):
        cursor = self.connection.cursor()
        cursor.execute("DROP INDEX IF EXISTS {column}_idx".format(column=self.index_name(column)))

    def recreate_table(self):
        self.drop_table()
        self.create_table()

    def insert(self, rows):
        cursor = self.connection.cursor()

        if not isinstance(rows, list):
            rows = [rows]

        to_type = lambda data, typename: int(data) if typename == "INTEGER" else safe_utf8(data)
        serializer = lambda row: [to_type(row.get(column), typename) for column, typename in self.schema.items()]
        cursor.executemany("INSERT INTO {table} VALUES({values})"
                           .format(table=self.table_name,
                                   values=", ".join(['?'] * len(self.schema))),
                           map(serializer, rows))

    def delete(self, condition):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM {table} WHERE {condition}"
                       .format(table=self.table_name,
                               condition=condition))

    def select(self, where=None):
        if where and not isinstance(where, dict):
            raise Exception("Invalid 'where' argument in select. Needs to be None or a dict")

        if where:
            where = " AND ".join("{column}={quote}{value}{quote}"
                                 .format(column=column,
                                         quote="" if self.schema[column] == "INTEGER" else "'",
                                         value=value) for column, value in where.items())

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM {table} WHERE {where}"
                       .format(table=self.table_name,
                               where=where))
        return cursor.fetchall()

    def count(self, condition=None):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM {table} {condition}"
                       .format(table=self.table_name,
                               condition='' if condition is None else "WHERE {}".format(condition)))
        return cursor.fetchone()[0]

    # def get_group_concat_by_key(self, key, column):
    #     """
    #     Concatenates all `array_column` values for each key
    #
    #     key    column         key    group_concat
    #     -----  -----      =>  -----  -----------
    #     1      '[1, 2]'       1      '[1, 2];[1, 3]'
    #     1      '[1, 3]'       2      '[8]'
    #     2      '[8]'
    #
    #     Note that the aggregated result might *not* be proper JSON (as in the
    #     above example)
    #     """
    #     self.create_index(column)
    #     cursor = self.connection.cursor()
    #     return cursor.execute("""SELECT {}, GROUP_CONCAT({}, ';')
    #                              FROM {} GROUP BY {}"""
    #                           .format(key, column, self.table_name, key))


class MemoriesMovies(MemoriesTable):
    def __init__(self):
        super(MemoriesMovies, self).__init__(table_name="mmr_movies",
                                             schema={"title": "TEXT",
                                                     "year": "INTEGER",
                                                     #  "country": "TEXT",
                                                     "url": "TEXT",
                                                     "description": "TEXT"})

    def insert(self, rows):
        # transform country
        pass
