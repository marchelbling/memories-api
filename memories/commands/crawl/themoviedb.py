import json
import os
import string
from crawler import Crawler
from db.models import MemoriesMovies, MemoriesTvs
from settings import Config


class TheMoviedbCrawler(Crawler):
    API_KEY = Config.get('themoviedb', 'token')
    REQUEST_DELAY = 0.5
    SERVICE = 'themoviedb'
    LETTERS = ' 0123456789' + string.ascii_lowercase

    @classmethod
    def api_url(cls, uid, subpoint=''):
        return 'http://api.themoviedb.org/3/{category}/{uid}{subpoint}?api_key={key}'\
                .format(category=cls.CATEGORY, uid=uid, subpoint=subpoint, key=cls.API_KEY)

    @classmethod
    def pretty_url(cls, uid):
        return 'http://themoviedb.org/{category}/{uid}'.format(category=cls.CATEGORY, uid=uid)

    @classmethod
    def get_from_api(cls, uid):
        response = cls.REQUESTER.get(cls.api_url(uid))
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            return {}

    @classmethod
    def get_uid(cls, url):
        return os.path.basename(url)

    @classmethod
    def search_url(cls, year, query, page=None):
        return 'http://api.themoviedb.org/3/search/{category}?api_key={api_key}&query={query}&{year_filter}={year}&page={page}'\
               .format(category=cls.CATEGORY,
                       year_filter=cls.YEAR_FILTER,
                       api_key=cls.API_KEY,
                       year=year,
                       query=query,
                       page=page or '1')

    @classmethod
    def urls(cls, year):
        for letter in cls.LETTERS:
            cls.page_count = 0  # will be set upon first transform
            yield cls.search_url(year, query=letter)
            for page in xrange(2, cls.page_count + 1):
                yield cls.search_url(year, query=letter, page=page)

    @classmethod
    def update(cls, content):
        response = json.loads(content)
        if cls.page_count == 0:
            cls.page_count = response['total_pages']

    @classmethod
    def candidate_urls(cls, content):
        response = json.loads(content)
        results = response['results']
        results = [result['id'] for result in results]
        return map(cls.pretty_url, results)

    @classmethod
    def artists(cls, url):
        response = cls.fetch_url(url)
        if response.status_code == 200:
            credits = json.loads(response.content)
            return ([c['name'] for c in credits.get('crew', []) if c['department'] == 'Directing'][:1] or
                    [c['name'] for c in credits.get('crew', []) if c['department'] == 'Producer'][:1]) + \
                   [u'{}{}'.format(c['name'], u' ({})'.format(c['character']) if c.get('character') else '')
                    for c in credits.get('cast', [])[:5]]
        else:
            return []

    @classmethod
    def french_title(cls, url):
        response = cls.fetch_url(url)
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
    def retrieve(cls, url):
        uid = cls.get_uid(url)
        content = cls.get_from_api(uid)

        year = lambda x: int(x) if x else None
        return {
            'title': content['name'],
            'year': year(content.get('first_air_date', '')[:4]),
            'url': url,
            'summary': content.get('overview', ''),
            'artists': cls.artists(cls.api_url(uid, subpoint='/credits')),
        }


class TheMoviedbMovieCrawler(TheMoviedbCrawler):
    CATEGORY = 'movie'
    MODEL = MemoriesMovies
    YEAR_FILTER = 'year'

    @classmethod
    def retrieve(cls, url):
        uid = cls.get_uid(url)
        content = cls.get_from_api(uid)

        year = lambda x: int(x) if x else None
        french_title = cls.french_title(cls.api_url(uid, subpoint='/alternative_titles'))
        french_title = u' ({})'.format(french_title) if french_title else ''
        return {
            'title': content.get('title', content['original_title']) + french_title,
            'year': year(content.get('release_date', '')[:4]),
            'url': url,
            'summary': content.get('overview', ''),
            'artists': cls.artists(cls.api_url(uid, subpoint='/credits')),
        }
