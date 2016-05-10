import requests
import time
import peewee


def wait(method):
    def clocked(self, *args, **kwargs):
        delay = getattr(self.__class__, 'REQUEST_DELAY', 0)
        if delay and getattr(self, '_clock', None):
            elapsed = time.time() - self._clock
            if elapsed < delay:
                time.sleep(delay - elapsed)
        result = method(self, *args, **kwargs)
        self._clock = time.time()
        return result
    return clocked


class Crawler(object):
    def __init__(self):
        self.requester = requests

    def crawl(self, year):
        for url in self.urls(year):
            response = self.fetch_url(url)
            if response.status_code == 200:
                self.store(self.transform(response.content))
                self.update(response.content)
            else:
                print(response.content)

    @wait
    def fetch_url(self, url):
        return self.requester.get(url)

    def transform(self, content):
        raise NotImplementedError

    def update(self, content):
        pass

    def store(self, entries):
        def store_entry(data):
            Model = self.__class__.MODEL
            try:
                Model.get(url=data['url']).update(**data).execute()
            except Model.DoesNotExist:
                Model.create(**data)
            except peewee.IntegrityError:
                print(u'integrity failure: {}'.format(data))

        map(store_entry, entries)
