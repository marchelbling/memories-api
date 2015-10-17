import falcon
import re
import os
import json
from collections import defaultdict


class SearchResource:
    CATEGORIES = defaultdict(lambda: 'all', {
        'movie': 'movies',
        'movies': 'movies',
        'tv': 'tvs',
        'tvs': 'tvs',
    })

    def search(self, pattern, category, limit=None):
        return {'result': self.rank(self.match(pattern, category, limit))}

    def match(self, pattern, category, limit=None):
        regex = re.compile(pattern, re.IGNORECASE)
        is_match = lambda line: re.search(regex, line)

        with open(os.path.join('/searchdata', category), 'r') as content:
            result = list(set(filter(is_match, content)))
        return map(json.loads, result[:limit])

    def rank(self, results):
        return results

    def on_get(self, req, resp):
        category = SearchResource.CATEGORIES[req.get_param('category')]
        pattern = req.get_param('pattern')
        limit = req.get_param_as_int('limit') or 10

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(self.search(pattern, category, limit))


app = falcon.API()
search = SearchResource()
app.add_route('/search', search)
