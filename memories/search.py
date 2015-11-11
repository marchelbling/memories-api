from db import MemoriesMovies, MemoriesTvs, MemoriesComics, MemoriesTable
import os
import json
import subprocess
from collections import defaultdict


class Search:
    CATEGORIES = defaultdict(lambda: 'all', {
        'movies': MemoriesMovies(),
        'movie': MemoriesMovies(),
        'tvs': MemoriesTvs(),
        'tv': MemoriesTvs(),
        'comics': MemoriesComics(),
        'comic': MemoriesComics(),
    })

    @staticmethod
    def content(category):
        return os.path.join('/data/memories-data', category)

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
        _category = Search.CATEGORIES[category]
        if isinstance(_category, MemoriesTable):
            matches = _category.match(pattern, limit)
        else:
            matches = Search.match(pattern, _category, limit)
        return json.dumps({'result': Search.rank(matches), 'category': category})
