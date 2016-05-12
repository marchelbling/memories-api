import datetime
import os

from db.models import *
from commands.crawl.themoviedb import TheMoviedbMovieCrawler


if __name__ == '__main__':
    def update(movie):
        uid = os.path.basename(movie.url)
        movie.artists = crawler.artists(TheMoviedbMovieCrawler.api_url(uid, subpoint='/credits'))
        movie.save()

    crawler = TheMoviedbMovieCrawler()
    map(update, MemoriesMovies.select()
                              .where(MemoriesMovies.updated_at < datetime.datetime(2016, 5, 12))
                              .iterator())
