import datetime
import json
from peewee import *
from settings import Config
from playhouse.shortcuts import model_to_dict, dict_to_model


class ArrayField(Field):
    db_field = 'array'

    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        return json.loads(value) if value else []


class MemoriesBaseModel(Model):
    url = CharField(null=False, unique=True)
    title = CharField(null=False)
    year = IntegerField(null=True)
    summary = TextField(null=True)
    artists = ArrayField(True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = Config.db()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        super(MemoriesBaseModel, self).save(*args, **kwargs)

    @classmethod
    def match(cls, pattern, limit=None):
        return map(model_to_dict,
                   cls.select()\
                      .where(cls.title.contains(pattern))
                      .limit(limit))


class MemoriesMovies(MemoriesBaseModel):
    class Meta:
        db_name = 'mmr_movies'


class MemoriesTvs(MemoriesBaseModel):
    class Meta:
        db_name = 'mmr_tvs'


class MemoriesComics(MemoriesBaseModel):
    class Meta:
        db_name = 'mmr_comics'


# ensure that tables exists
Config.db().create_tables([MemoriesMovies, MemoriesTvs, MemoriesComics], safe=True)