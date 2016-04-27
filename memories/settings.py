import os
from ConfigParser import RawConfigParser


class Config:
    settings = RawConfigParser()
    settings.read("config.rc")

    @staticmethod
    def get(*attr):
        return Config.settings.get(*attr)

    @staticmethod
    def db():
        db_path = os.path.join(Config.get("memories", "storage"),
                               Config.get("memories", "db_name"))
        return SqliteDatabase(db_path)
