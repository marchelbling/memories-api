import falcon
from api.search import SearchApi


app = falcon.API()
# search
app.add_route('/search', SearchApi())
