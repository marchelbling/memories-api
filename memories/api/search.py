import falcon
import json
from db.models import MemoriesMovies, MemoriesTvs, MemoriesComics
from utils import timehttp, safe_utf8


def search(pattern, category, limit):
    to_model = {
        'movies': MemoriesMovies(),
        'movie': MemoriesMovies(),
        'tvs': MemoriesTvs(),
        'tv': MemoriesTvs(),
        'comics': MemoriesComics(),
        'comic': MemoriesComics(),
    }

    def rank(results):
        return results

    def serialize(results):
        def apify(mmr):
            return {
                'title': mmr['title'],
                'url': mmr['url'],
                'created_at': mmr['created_at'].strftime('%Y-%m-%dT%H:%M:%S'),
                'updated_at': mmr['updated_at'].strftime('%Y-%m-%dT%H:%M:%S'),
                'year': mmr.get('year', None),
                'country': mmr.get('country', None),
                'artists': mmr.get('artists', []),
                'summary': mmr.get('summary', '')
            }
        return map(apify, results)

    try:
        matches = to_model[category].match(safe_utf8(pattern), limit)
    except KeyError:
        matches = []
    return json.dumps({'result': serialize(rank(matches)), 'category': category})


class SearchApi:
    @timehttp
    def on_get(self, req, resp):
        category = req.get_param('category')
        pattern = req.get_param('pattern')
        limit = req.get_param_as_int('limit') or 10

        # always return a response (empty if search failed)
        resp.status = falcon.HTTP_200
        resp.body = search(pattern=pattern, category=category, limit=limit)
