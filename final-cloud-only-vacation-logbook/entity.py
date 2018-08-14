# [START imports]
from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import json

# entity classes
class StockAsset(ndb.Model):
    user_id = ndb.StringProperty() # connection of who it belongs to
    giver_id = ndb.StringProperty(default=None) # if asset is gift from someone
    symbol = ndb.StringProperty()
    owned_count = ndb.FloatProperty()
    price_usd_open = ndb.StringProperty()
    last_updated = ndb.StringProperty()


class Account(ndb.Model):
    user_id = ndb.StringProperty() # this should be used as unique key
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    occupation = ndb.StringProperty()
    asset_count = ndb.IntegerProperty()
