# [START imports]
from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import json
from entity import DepartureHistory, Boat, Slip

# helper with datetime encoding in JSON


# entity handlers
class BoatHandler(webapp2.RequestHandler):
    # add a new boat
    def post(self):
        # user submits request with data for boat name, type, length
        data = json.loads(self.request.body)
        new_boat = Boat(name=data['name'], type=data['type'], length=data['length'], at_sea=True)

        new_boat.put() # add in db first so id is auto-generated
        new_boat.id = new_boat.key.urlsafe()
        new_boat.put()

        boat_dict = new_boat.to_dict()

        self.response.write(json.dumps(boat_dict))


    # get data for specific instance or list if id is not specified
    def get(self, id=None):
    	if(id):
    		data = ndb.Key(urlsafe=id).get()
    		boat_dict = data.to_dict()

    		self.response.write(json.dumps(boat_dict))
    	else:
    		self.response.write(json.dumps([d.to_dict() for d in Boat.query()]))



			




class SlipHandler(webapp2.RequestHandler):
    # add a new slip
    def post(self):
        # user submits request with data for slip number
        data = json.loads(self.request.body)
        new_slip = Slip(number=data['number'], current_boat=None, arrival_date=None, departure_history=[])

        new_slip.put()
        new_slip.id = new_slip.key.urlsafe()
        new_slip.put()

        slip_dict = new_slip.to_dict()

        self.response.write(json.dumps(slip_dict))


    # get data for specific instance or list if id is not specified
    def get(self, id=None):
    	if(id):
    		data = ndb.Key(urlsafe=id).get()

    		slip_dict = data.to_dict()

    		self.response.write(json.dumps(slip_dict))
    	else:
    		self.response.write(json.dumps([d.to_dict() for d in Slip.query()]))





class SlipWithBoatHandler(webapp2.RequestHandler):
	# put a boat into a slip (body)
	def put(self, id=None):
		if(not id):
			self.response.set_status(400)
			self.response.write('Require Slip ID')


		put_boat_data = json.loads(self.request.body)
		slip_data = ndb.Key(urlsafe=id).get()

		# returns 403 forbidden if slip is already occupied
		if(slip_data.current_boat):
			self.response.set_status(403)
			self.response.write('Error: Slip is occupied')
		else:
			boat_data = ndb.Key(urlsafe=put_boat_data['boat_id']).get()

			# update boat status in db
			boat_data.at_sea = False
			boat_data.put()

			# update slip data (boat id, arrival date)
			slip_data.current_boat = put_boat_data['boat_id']
			slip_data.arrival_date = put_boat_data['arrival_date']
			slip_data.put()
			self.response.write(json.dumps(slip_data.to_dict()))

		













class DeleteAll(webapp2.RequestHandler):
	def get(self):
		ndb.delete_multi(Boat.query().fetch(keys_only=True))
		ndb.delete_multi(Slip.query().fetch(keys_only=True))
		ndb.delete_multi(DepartureHistory.query().fetch(keys_only=True))

