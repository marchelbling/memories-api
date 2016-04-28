import os
from ConfigParser import RawConfigParser
from peewee import SqliteDatabase


class Config:
    def find_config_file():
        path = os.path.abspath(os.path.curdir)
        filename = 'config.rc'
        while path and not os.path.exists(os.path.join(path, filename)):
            path = os.path.abspath(os.path.join(path, '../'))
        return os.path.join(path, filename)

    settings = RawConfigParser()
    settings.read(find_config_file())


    @staticmethod
    def get(*attr):
        return Config.settings.get(*attr)

    @staticmethod
    def db():
        db_path = os.path.join(Config.get("memories", "storage"),
                               Config.get("memories", "db_name"))
        return SqliteDatabase(db_path)
