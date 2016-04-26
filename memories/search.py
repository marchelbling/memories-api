from db import MemoriesMovies, MemoriesTvs, MemoriesComics, MemoriesTable
import os
import json
import subprocess
from collections import defaultdict


class Search:
    CATEGORIES = {
        'movies': MemoriesMovies(),
        'movie': MemoriesMovies(),
        'tvs': MemoriesTvs(),
        'tv': MemoriesTvs(),
        'comics': MemoriesComics(),
        'comic': MemoriesComics(),
    }

    @staticmethod
    def content(category):
        return os.path.join('/data/memories-data', category)

    @staticmethod
    def rank(results):
        def reformat(result):
            result.setdefault('artists', [])
            result.setdefault('summary', '')
            return result
        return map(reformat, results)

    @staticmethod
    def get(pattern, category, limit):
        handler = Search.CATEGORIES.get(category)
        if isinstance(handler, MemoriesTable):
            matches = handler.match(pattern, limit)
        else:
            matches = []
        return json.dumps({'result': Search.rank(matches), 'category': category})
