import falcon
import os
import json
import subprocess
from collections import defaultdict


class Search:
    CATEGORIES = defaultdict(lambda: 'all', {
        'movie': 'movies',
        'movies': 'movies',
        'tv': 'tvs',
        'tvs': 'tvs',
    })

    @staticmethod
    def load_category(category):
        with open(os.path.join('/searchdata', category), 'r') as content:
            return content.readlines()

    def __init__(self):
        categories = Search.CATEGORIES.values() + [Search.CATEGORIES.default_factory()]
        self.data = {category: Search.load_category(category) for category in categories}

    def search(self, pattern, category, limit):
        return {'result': self.rank(self.match(pattern, category, limit))}

    def match(self, pattern, category, limit):
        try:
            results = subprocess.check_output(['grep',
                                               '-m {}'.format(limit),
                                               '-i',
                                               pattern,
                                               os.path.join('/searchdata', category)])\
                                .split('\n')
        except subprocess.CalledProcessError:
            results = "[]"
        return map(json.loads, results)

    def rank(self, results):
        return results

    def on_get(self, req, resp):
        category = Search.CATEGORIES[req.get_param('category')]
        pattern = req.get_param('pattern')
        limit = req.get_param_as_int('limit') or 10

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(self.search(pattern, category, limit))


app = falcon.API()
search = Search()
app.add_route('/search', search)
