import os
import json
import string
import requests
from bs4 import BeautifulSoup
from crawler import Crawler
from cleaner import comicsify
from db.models import MemoriesComics

_p = os.path


class BedethequeCrawler(Crawler):
    REQUEST_DELAY = 1.25
    SERVICE = 'bedetheque'
    BASE_URL = 'http://bedetheque.com'
    SEARCH_URL = 'http://www.bedetheque.com/search/albums?'\
                 'RechIdSerie=&RechIdAuteur=&csrf_token_bedetheque={token}&'\
                 'RechSerie=&RechTitre=&RechEditeur=&RechCollection=&RechStyle=&RechAuteur=&'\
                 'RechISBN=&RechParution=&RechOrigine=&RechLangue=&RechMotCle=&'\
                 'RechDLDeb={month:02d}/{year}&RechDLFin={month:02d}/{year}&RechCoteMin=&RechCoteMax=&RechEO=0'
    MODEL = MemoriesComics

    def __init__(self):
        super(BedethequeCrawler, self).__init__()

    def new_session(self):
        client = requests.session()
        client.get(BedethequeCrawler.BASE_URL)
        client.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) '\
                                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'
        client.headers['Referer'] = 'http://www.bedetheque.com'
        client.headers['Host'] = 'www.bedetheque.com'
        self.requester = client

    def urls(self, year, month=None):
        months = [month] if month else range(1, 12 + 1)

        for month in months:
            self.new_session()
            yield BedethequeCrawler.SEARCH_URL.format(token=self.requester.cookies['csrf_cookie_bedetheque'],
                                                      month=month, year=year)

    def transform(self, content):
        def text(node):
            return node.text if node else ''

        def titlify(soup):
            try:
                return soup.find('meta', {'itemprop': 'name'})['content']
            except:
                lis = soup.find('ul', {'class': 'infos-albums'}).find_all('li')
                texts = [li.text for li in lis]
                texts = [text for text in texts if 'Titre' in text]
                return texts[0].replace('Titre : ', '').strip() if texts else ''

        def extract(link):
            url = link.get('href')
            if not 'bedetheque.com/BD' in url:
                return {}

            details = self.fetch_url(url)
            soup = BeautifulSoup(unicode(details.content, 'utf8', errors='replace'), 'lxml')
            artists = filter(None,
                                [text(soup.find('span', {'itemprop': 'author'})),
                                text(soup.find('span', {'itemprop': 'illustrator'}))])
            summary = text(soup.find('p', {'id': 'p-serie'}))
            year = text(soup.find('span', {'class': 'annee'}))
            title = titlify(soup)

            return {
                'url': url,
                'title': title,
                'year': int(year) if year else None,
                'artists': artists,
                'summary': summary
            }
        soup = BeautifulSoup(unicode(content, 'utf8', errors='replace'), 'lxml')
        return filter(lambda comic: comic and comic.get('title'),
                      map(extract,
                          soup.find_all('a', title='tooltip')))
