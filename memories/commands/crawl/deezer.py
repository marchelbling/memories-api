import json
import os
import string
from crawler import Crawler
from db.models import MemoriesMusics
from settings import Config


class DeezerCrawler(Crawler):
    REQUEST_DELAY = 0.11
    SERVICE = 'deezer'
    MODEL = MemoriesMusics

    @classmethod
    def api_url(cls, uid):
        return 'http://api.deezer.com/album/{uid}'.format(uid=uid)

    @classmethod
    def pretty_url(cls, uid):
        return 'http://deezer.com/album/{uid}'.format(uid=uid)

    @classmethod
    def urls(cls, _):
        uid = 100
        max_uid = 4000000
        while uid < max_uid:
            yield cls.api_url(uid)
            uid += 1

    @classmethod
    def transform(cls, content):
        response = json.loads(content)
        return [None] if cls.exists(response['link']) else [cls.parse(response)]

    @classmethod
    def parse(cls, response):
        def summarize(response):
            genres = map(lambda genre: genre['name'],
                         response.get('genres', {}).get('data', []))
            return u'\n'.join(filter(None,
                                    [u'Genres: {}'.format(u', '.join(genres[:5])) if genres else None,
                                     u'#Tracks: {}'.format(response['nb_tracks']) if response.get('nb_tracks') else None,
                                     u'Label: {}'.format(response['label']) if response.get('label') else None]))

        year = lambda x: int(x) if x else None
        return {
            'title': response['title'],
            'year': year(response.get('release_date', '')[:4]),
            'url': response['link'],
            'summary': summarize(response),
            'artists': filter(None, [response.get('artist', {}).get('name', '')]),
        }
