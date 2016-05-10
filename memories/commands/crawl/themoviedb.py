import os
import json
import string
from crawler import Crawler
from db.models import MemoriesMovies, MemoriesTvs
from settings import Config

_p = os.path


class TheMoviedbCrawler(Crawler):
    API_KEY = Config.get('themoviedb', 'token')
    REQUEST_DELAY = 0.5
    SERVICE = 'themoviedb'
    LETTERS = ' 0123456789' + string.ascii_lowercase

    def __init__(self):
        super(TheMoviedbCrawler, self).__init__()

    def base_url(self):
        return 'http://api.themoviedb.org/3/search/{category}?api_key={api_key}&query={{query}}&{year_filter}={{year}}&page={{page}}'\
               .format(category=self.__class__.CATEGORY,
                       year_filter=self.__class__.YEAR_FILTER,
                       api_key=self.__class__.API_KEY)

    def url(self, year, query, page=None):
        return self.base_url().format(year=year,
                                      query=query,
                                      page=page or '1')

    def urls(self, year):
        for letter in self.__class__.LETTERS:
            print 'letter: {}'.format(letter)
            self.page_count = 0  # will be set upon first transform
            yield self.url(year, letter)
            for page in xrange(2, self.page_count + 1):
                yield self.url(year, letter, page)

    def transform(self, content):
        response = json.loads(content)
        if self.page_count == 0:
            self.page_count = response['total_pages']
        return filter(None,
                      map(self.extract, response['results']))

    def summary(self, url):
        response = self.fetch_url(url)
        if response.status_code == 200:
            return json.loads(response.content).get('overview', '')
        else:
            return ''

    def artists(self, url):
        response = self.fetch_url(url)
        if response.status_code == 200:
            credits = json.loads(response.content)
            return [c['name'] for c in credits.get('crew', [])[:1]] + \
                   [u'{} ({})'.format(c['name'], c.get('character', '')) for c in credits.get('cast', [])[:5]]
        else:
            return []

    def french_title(self, url):
        response = self.fetch_url(url)
        if response.status_code == 200:
            try:
                return filter(lambda entry: entry['iso_3166_1'] == 'FR',
                              json.loads(response.content))[0].get('title', '')
            except:
                return ''
        else:
            return ''


class TheMoviedbTvCrawler(TheMoviedbCrawler):
    CATEGORY = 'tv'
    MODEL = MemoriesTvs
    YEAR_FILTER = 'first_air_date_year'

    @classmethod
    def api_url(cls, uid, subpoint=''):
        return 'http://api.themoviedb.org/3/tv/{uid}{subpoint}?api_key={key}'\
                .format(uid=uid, subpoint=subpoint, key=cls.API_KEY)

    @staticmethod
    def pretty_url(uid):
        return 'http://themoviedb.org/tv/{uid}'.format(uid=uid)

    def extract(self, result):
        uid = result['id']
        url = TheMoviedbTvCrawler.pretty_url(uid)

        Model = self.__class__.MODEL
        try:
            Model.get(url=url)
        except Model.DoesNotExist:
            year = lambda x: int(x) if x else None
            return {
                'title': result['name'],
                'year': year(result.get('first_air_date', '')[:4]),
                'url': url,
                'summary': self.summary(TheMoviedbTvCrawler.api_url(uid)),
                'artists': self.artists(TheMoviedbTvCrawler.api_url(uid, subpoint='credits')),
            }
        else:
            return {}


class TheMoviedbMovieCrawler(TheMoviedbCrawler):
    CATEGORY = 'movie'
    MODEL = MemoriesMovies
    YEAR_FILTER = 'year'

    @classmethod
    def api_url(cls, uid, subpoint=''):
        return 'http://api.themoviedb.org/3/movie/{uid}{subpoint}?api_key={key}'\
                .format(uid=uid, subpoint=subpoint, key=cls.API_KEY)

    @staticmethod
    def pretty_url(uid):
        return 'http://themoviedb.org/movie/{uid}'.format(uid=uid)

    def extract(self, result):
        uid = result['id']
        url = TheMoviedbMovieCrawler.pretty_url(uid)

        Model = self.__class__.MODEL
        try:
            Model.get(url=url)
        except Model.DoesNotExist:
            year = lambda x: int(x) if x else None
            french_title = self.french_title(TheMoviedbMovieCrawler.api_url(uid, subpoint='/alternative_titles'))
            french_title = u' ({})'.format(french_title) if french_title else ''
            return {
                'title': result.get('title', result['original_title']) + french_title,
                'year': year(result.get('release_date', '')[:4]),
                'url': url,
                'summary': self.summary(TheMoviedbMovieCrawler.api_url(uid)),
                'artists': self.artists(TheMoviedbMovieCrawler.api_url(uid, subpoint='/credits')),
            }
        else:
            return {}
