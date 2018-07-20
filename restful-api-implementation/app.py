# [START imports]
from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import json
from entity import DepartureHistory, Boat, Slip
from handler import BoatHandler, SlipHandler, SlipWithBoatHandler, DeleteAll


# main front-end UI page
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("hello")

# [START app]
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boats', BoatHandler),
    ('/boats/(.*)', BoatHandler),
    ('/slips/(.*)/boat', SlipWithBoatHandler),
    ('/slips', SlipHandler),
    ('/slips/(.*)', SlipHandler),
    
    ('/deleteall', DeleteAll)
], debug=True)
# [END app]