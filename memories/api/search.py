import falcon
import json
from db.models import MemoriesMovies, MemoriesTvs, MemoriesComics
from utils import timehttp, safe_utf8


def search(pattern, category, limit):
    to_model = {
        'movies': MemoriesMovies,
        'movie': MemoriesMovies,
        'tvs': MemoriesTvs,
        'tv': MemoriesTvs,
        'comics': MemoriesComics,
        'comic': MemoriesComics,
    }

    try:
        handler = to_model[category]
        matches = map(lambda model: model.serialize(),
                      handler.match(safe_utf8(pattern), limit))
    except KeyError:
        matches = []
    return json.dumps({
        'result': matches,
        'category': category
    })


class SearchApi:
    @timehttp
    def on_get(self, req, resp):
        category = req.get_param('category')
        pattern = req.get_param('pattern')
        limit = req.get_param_as_int('limit') or 10

        # always return a response (empty if search failed)
        resp.status = falcon.HTTP_200
        resp.body = search(pattern=pattern, category=category, limit=limit)
