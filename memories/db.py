import datetime
from peewee import *
from settings import Config


class MemoriesBaseModel(Model):
    updated_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)
    title = CharField(null=False)
    url = CharField(null=False)
    year = IntegerField()
    summary = TextField()
    # FIXME: artists

    class Meta:
        database = Config.db()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()


class MemoriesMovies(MemoriesBaseModel):
    pass


class MemoriesTvs(MemoriesBaseModel):
    pass

class MemoriesComics(MemoriesBaseModel):
    pass
