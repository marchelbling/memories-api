import falcon
from utils import timehttp
from search import Search


def safe_utf8(string):
    def safe_decode(string):
        try:
            return unicode(string, 'utf8')
        except UnicodeError:
            try:
                return unicode(string, 'latin1')
            except UnicodeError:
                return unicode(string, 'utf8', 'replace')

    if not isinstance(string, unicode):
        string = safe_decode(string)

    return string.encode('utf8')


class SearchAPI:
    @timehttp
    def on_get(self, req, resp):
        category = req.get_param('category')
        pattern = req.get_param('pattern')
        limit = req.get_param_as_int('limit') or 10

        # always return a response (empty if search failed)
        resp.status = falcon.HTTP_200
        resp.body = Search.get(pattern=pattern, category=category, limit=limit)


app = falcon.API()
# search
search_api = SearchAPI()
app.add_route('/search', search_api)
