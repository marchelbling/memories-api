# coding=utf-8
import datetime
import json
import re

from collections import OrderedDict
from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model

from settings import Config


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

    def serialize(self):
        cls = self.__class__
        return {
            'title': cls.clean_title(self.title),
            'url': self.url,
            'updated_at': self.updated_at.strftime('%Y-%m-%dT%H:%M:%S'),
            'year': self.year or None,
            'artists': cls.clean_artists(self.artists or []),
            'summary': (self.summary or '').strip()
        }

    @classmethod
    def sample(cls, size=10, serialized=True):
        formatter = lambda m: m.serialize() if serialized else m
        return map(formatter,
                   cls.select().order_by(fn.Random()).limit(size))

    @classmethod
    def clean_title(cls, title):
        return title

    @classmethod
    def clean_artists(cls, artists):
        return artists

    @classmethod
    def match(cls, pattern, limit=None):
        return cls.select()\
                  .where(cls.title.contains(pattern))\
                  .order_by(cls.year.desc())\
                  .limit(limit)


class MemoriesMovies(MemoriesBaseModel):
    class Meta:
        db_name = 'mmr_movies'


class MemoriesTvs(MemoriesBaseModel):
    class Meta:
        db_name = 'mmr_tvs'


class MemoriesComics(MemoriesBaseModel):
    class Meta:
        db_name = 'mmr_comics'

    @classmethod
    def clean_title(cls, title):
        def find_parentheses(string):
            PARENTHESIS_GROUP = re.compile(' \((.*?)\)', re.UNICODE)
            return PARENTHESIS_GROUP.findall(string)

        def remove_parentheses(string):
            PARENTHESIS = re.compile(' \(.*?\)', re.UNICODE)
            return PARENTHESIS.sub(u'', string)

        def tokenify(title):
            TOKEN = re.compile(' - \s*(?![^()]*\))', re.UNICODE)  # handle e.g. "Tarzan (4e Série - Sagédition) (Géant)"
            return filter(None,
                          map(lambda token: token.strip(),
                              TOKEN.split(title)))

        def authorify(title):
            return u'{} ({})'.format(*title.replace(u'(AUT) ', u'').split(u' - ', 1)[::-1]) \
                    if title.startswith(u'(AUT)') else title

        def prefixify(title):
            """ Only keeps parenthesised tokens that are prefixes """
            PREFIX = set([u"l'", u"le", u"la", u"les",
                          u"du", u"de", u"d'", u"des",
                          u"un", u"une",
                          u"the", u"a", u"an", "of"]) # case insensitive

            tokens = tokenify(title)
            output = []
            for token in tokens:
                parentheses = find_parentheses(token)
                token = token.split(u'(', 1)[0]
                if not token:
                    continue
                for parenthesis in parentheses:
                    last = parenthesis.rsplit(u' ', 1)[-1]  # handle e.g. "(Les aventures de)"
                    if last.lower() in PREFIX:
                        if u' ' not in parenthesis:
                            parenthesis = parenthesis.capitalize()
                        token = parenthesis + u' ' + token
                    else:
                        token += u' (' + parenthesis + u')'
                output.append(token)

            return u' - '.join(output)

        def unify(title):
            """ Split on dash and only keeps first occurence of tokens """
            tokens = tokenify(title)
            groups = OrderedDict()
            for token in tokens:
                groups.setdefault(remove_parentheses(token.lower()).strip(), []).append(token)
            # for each lower+no_parenthesis token, take the *longest* element
            return u' - '.join(sorted(values)[-1] for values in groups.values())

        return prefixify(unify(authorify(title))).strip()

    @classmethod
    def clean_artists(cls, artists):
        return filter(lambda artist: artists != u'<Indéterminé>',
                      map(lambda artist: ' '.join(artist.split(',')[::-1]).strip(),
                          artists))


class MemoriesMusics(MemoriesBaseModel):
    class Meta:
        db_name = 'mmr_musics'


# ensure that tables exists
Config.db().create_tables([MemoriesMovies, MemoriesTvs, MemoriesComics, MemoriesMusics], safe=True)
