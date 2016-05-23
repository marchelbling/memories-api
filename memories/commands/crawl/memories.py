# -*- coding: utf-8 -*-

import argparse
from themoviedb import TheMoviedbTvCrawler, TheMoviedbMovieCrawler
from bedetheque import BedethequeCrawler
from deezer import DeezerCrawler


def parse_options():
    parser = argparse.ArgumentParser(description='Crawl cultural material')
    parser.add_argument('--tv', action='store_true', default=False,
                        help='Crawl tv shows list')
    parser.add_argument('--movie', action='store_true', default=False,
                        help='Crawl movies list')
    parser.add_argument('--comics', action='store_true', default=False,
                        help='Crawl comics list')
    parser.add_argument('--music', action='store_true', default=False,
                        help='Crawl music list')
    parser.add_argument('--year', default=None, required=True,
                        help='Crawl specific year')
    return parser.parse_args()


def main():
    options = parse_options()
    handlers = []

    if options.tv:
        handlers.append(TheMoviedbTvCrawler())
    if options.movie:
        handlers.append(TheMoviedbMovieCrawler())
    if options.comics:
        handlers.append(BedethequeCrawler())
    if options.music:
        handlers.append(DeezerCrawler())

    map(lambda handler: handler.crawl(options.year),
        handlers)

if __name__ == '__main__':
    main()
