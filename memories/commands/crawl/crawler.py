import peewee
import requests
import time


def wait(method):
    def clocked(obj, *args, **kwargs):
        delay = getattr(obj, 'REQUEST_DELAY', getattr(obj.__class__, 'REQUEST_DELAY', 0))
        if delay and getattr(obj, '_clock', None):
            elapsed = time.time() - obj._clock
            if elapsed < delay:
                time.sleep(delay - elapsed)
        result = method(obj, *args, **kwargs)
        obj._clock = time.time()
        return result
    return clocked


class Crawler(object):
    REQUESTER = requests

    @classmethod
    def crawl(cls, year):
        for url in cls.urls(year):
            response = cls.fetch_url(url)
            if response.status_code == 200:
                cls.store(cls.transform(response.content))
                cls.update(response.content)
            else:
                print(response.content)

    @classmethod
    @wait
    def fetch_url(cls, url):
        return cls.REQUESTER.get(url)

    @classmethod
    def transform(cls, content):
        return filter(None,
                      map(cls.exists,
                          cls.candidate_urls(content)))

    @classmethod
    def update(cls, content):
        pass

    @classmethod
    def exists(cls, url):
        Model = cls.MODEL
        try:
            # if url is already registered then skip it
            Model.get(url=url)
        except Model.DoesNotExist:
            return cls.retrieve(url)
        else:
            return {}

    @classmethod
    def store(cls, entries):
        def store_entry(data):
            Model = cls.MODEL
            try:
                Model.get(url=data['url']).update(**data).execute()
            except Model.DoesNotExist:
                Model.create(**data)
            except peewee.IntegrityError:
                print(u'integrity failure: {}'.format(data))

        map(store_entry, entries)
