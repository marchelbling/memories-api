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
    def content(category):
        return os.path.join('/data/memories', category)

    @staticmethod
    def match(pattern, category, limit):
        try:
            results = subprocess.check_output(['grep',
                                               '-m {}'.format(limit),
                                               '-i',
                                               pattern,
                                               Search.content(category)])\
                                .split('\n')
        except Exception:  # failsafe all exceptions
            results = []
        return map(json.loads,
                   filter(None, results))  # filter empty lines

    @staticmethod
    def rank(results):
        return results

    @staticmethod
    def get(pattern, category, limit):
        category = Search.CATEGORIES[category]
        return json.dumps({'result': Search.rank(Search.match(pattern, category, limit)),
                           'category': category})
