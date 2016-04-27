import falcon
from utils import timehttp
from search import Search


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
app.add_route('/search', SearchAPI())
