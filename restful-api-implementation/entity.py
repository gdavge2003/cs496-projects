# [START imports]
from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import json

# entity classes
class DepartureHistory(ndb.Model):
    departure_date = ndb.StringProperty()
    departure_boat = ndb.StringProperty()


class Boat(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(default=None)
    length = ndb.IntegerProperty(default=None)
    at_sea = ndb.BooleanProperty()


class Slip(ndb.Model):
    id = ndb.StringProperty()
    number = ndb.IntegerProperty(required=True)
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty()
    departure_history = ndb.StructuredProperty(DepartureHistory, repeated=True)