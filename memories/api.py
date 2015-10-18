import falcon
from search import Search


class SearchAPI:
    def on_get(self, req, resp):
        category = req.get_param('category')
        pattern = req.get_param('pattern')
        limit = req.get_param_as_int('limit') or 10

        # always return a response (empty if search failed)
        resp.status = falcon.HTTP_200
        resp.body = Search.get(pattern=pattern, category=category, limit=limit)


app = falcon.API()
search_api = SearchAPI()
app.add_route('/search', search_api)
