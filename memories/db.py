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


class Config:
    config = RawConfigParser()
    config.read("config.rc")
    sql_types = {"INTEGER": "INTEGER",
                 "JSON":    "TEXT",
                 "TEXT":    "TEXT"}

    @staticmethod
    def get(*attr):
        return Config.config.get(*attr)

    @staticmethod
    def sql_type(typename):
        return Config.sql_types.get(typename, "TEXT")


class MemoriesDB(object):
    db = os.path.join(Config.get("memories", "storage"),
                      Config.get("memories", "db_name"))

    @staticmethod
    def get_connection():
        def dict_factory(cursor, row):
            return {column: row[index] for index, (column, _, _, _, _, _, _) in enumerate(cursor.description)}

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

    def columns(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM {table} LIMIT 1".format(table=self.table_name))
        return [column for (column, _, _, _, _, _, _) in cursor.description if column not in ('rowid', 'oid')]

    def table_schema(self):
        columns = ["{column} {type}".format(column=column, type=self.schema[column]) for column in self.columns()]
        unicity = ["UNIQUE({}) ON CONFLICT REPLACE".format(", ".join(self.unicity))] if self.unicity else []
        return ", ".join(columns + unicity)

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA cache_size = 20000;")
        cursor.execute("PRAGMA page_size = 4096;")
        cursor.execute("PRAGMA temp_store = MEMORY;")
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA locking_mode = NORMAL;")
        cursor.execute("CREATE TABLE IF NOT EXISTS {table} ({schema})"
                       .format(table=self.table_name, schema=self.table_schema()))

    def drop_table(self):
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS {table}".format(table=self.table_name))

    def index_name(self, column):
        return "_i_mmr_{table}_{column}".format(table=self.table_name, column=column)

    def create_index(self, column):
        if self.index_column:
            cursor = self.connection.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS {index} ON {table} ({column} ASC)"
                           .format(index=self.index_name(column),
                                   column=column,
                                   table=self.table_name))

    def drop_index(self, column):
        cursor = self.connection.cursor()
        cursor.execute("DROP INDEX IF EXISTS {index}".format(index=self.index_name(column)))

    def recreate_table(self):
        self.drop_table()
        self.create_table()

    def insert(self, rows):
        if not isinstance(rows, list):
            rows = [rows]

        columns = self.columns()
        typer = lambda typename: {"INTEGER": lambda value: int(value) if value else None}.get(typename, safe_utf8)
        serializer = lambda row: [typer(self.schema[column])(row.get(column)) for column in columns]

        cursor = self.connection.cursor()
        cursor.executemany("INSERT INTO {table} VALUES({values})"
                           .format(table=self.table_name,
                                   values=", ".join(['?'] * len(columns))),
                           map(serializer, rows))

    def delete(self, where):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM {table} WHERE {where}"
                       .format(table=self.table_name,
                               where=where))

    def select(self, where=None, limit=None):
        cursor = self.connection.cursor()
        sql = "SELECT * FROM {table}".format(table=self.table_name)
        if where:
            sql += " WHERE {condition}".format(condition=where)
        if limit:
            sql += " LIMIT {count}".format(count=limit)
        cursor.execute(sql)
        return cursor.fetchall()

    def count(self, where=None):
        cursor = self.connection.cursor()
        sql = "SELECT COUNT(*) FROM {table}".format(table=self.table_name)
        if where:
            sql += " WHERE {condition}".format(condition=where)
        cursor.execute(sql)
        return cursor.fetchone()

    def match(self, pattern, limit=None):
        return self.select(where="title LIKE '%{pattern}%' ORDER BY year DESC".format(pattern=safe_utf8(pattern)),
                           limit=limit)


class MemoriesMovies(MemoriesTable):
    def __init__(self):
        super(MemoriesMovies, self).__init__(table_name="mmr_movies",
                                             schema={"title": "TEXT",
                                                     "year": "INTEGER",
                                                     "url": "TEXT",
                                                     "metadata": "TEXT"})
        self.create_table()


class MemoriesTvs(MemoriesTable):
    def __init__(self):
        super(MemoriesTvs, self).__init__(table_name="mmr_tvs",
                                          schema={"title": "TEXT",
                                                  "year": "INTEGER",
                                                  "url": "TEXT",
                                                  "metadata": "TEXT"})
        self.create_table()


class MemoriesComics(MemoriesTable):
    def __init__(self):
        super(MemoriesComics, self).__init__(table_name="mmr_comics",
                                             schema={"title": "TEXT",
                                                     "year": "INTEGER",
                                                     "url": "TEXT",
                                                     "metadata": "TEXT"})
        self.create_table()
