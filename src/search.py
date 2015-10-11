import falcon


class SearchResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ('\nhello world\n\n')


app = falcon.API()
search = SearchResource()
app.add_route('/search', search)
