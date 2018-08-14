# [START imports]
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import webapp2
import json
import os
import string
import random
import urllib
import logging
from entity import StockAsset, Account

RETRIEVE_DATA_URL="https://www.googleapis.com/plus/v1/people/me"

# helper function
# checks whether user id is in db or not
def UserExists(user_id):
	for user in Account.query():
		if user.user_id == user_id:
			return True
		else:
			return False

# grabs the bearer token from user's auth header
def GetBearerToken(headers):
	logging.info(headers)
	if 'Authorization' in headers:
		return headers['Authorization'].split()[1]
	else:
		return ''

class AccountHandler(webapp2.RequestHandler):
	# gets account information of user_id
	def get(self, user_id):
		if UserExists(user_id):
			data = Account.get_by_id(user_id)
			self.response.write(json.dumps(data.to_dict()))
		elif len(user_id) == 0:
			self.response.status = 400
			self.response.write("Error: User_id must be specified in request.")
		else:
			self.response.status = 404
			self.response.write("Error: User " + user_id + " does not exist in database.")

	# updates account name, email or occupation. DOES NOT change any id or asset info
	def patch(self, user_id=None):

		if not user_id:
			self.response.status = 400
			self.response.write("Error: User_id must be specified in request.")
		elif not UserExists(user_id):
			self.response.status = 404
			self.response.write("Error: User does not exist in database.")
		else:
			# check correct token for identity. user cannot modify other users' data
			token = GetBearerToken(self.request.headers)
			header = {'Authorization': 'Bearer ' + token}
			results = urlfetch.fetch(
				url=RETRIEVE_DATA_URL,
				method=urlfetch.GET,
				headers=header
				)

			# Process retrieved data
			results = json.loads(results.content)
			logging.info("-------------------------------------------------")
			logging.info("-------------------------------------------------")
			logging.info("-------------------------------------------------")
			logging.info("-------------------------------------------------")
			logging.info(results)




#
# # entity handlers
# class BoatHandler(webapp2.RequestHandler):
# 	# add a new boat
# 	def post(self):
# 		# user submits request with data for boat name, type, length
# 		data = json.loads(self.request.body)
# 		new_boat = Boat(name=data['name'], type=data['type'], length=data['length'], at_sea=True)
#
# 		new_boat.put() # add in db first so id is auto-generated
# 		new_boat.id = new_boat.key.urlsafe()
# 		new_boat.put()
#
# 		boat_dict = new_boat.to_dict()
#
# 		self.response.write(json.dumps(boat_dict))
#
#
# 	# get data for specific instance or list if id is not specified
# 	def get(self, id=None):
# 		if(id):
# 			if(IsExist(id)):
# 				data = ndb.Key(urlsafe=id).get()
# 				boat_dict = data.to_dict()
# 				self.response.write(json.dumps(boat_dict))
# 			else:
# 				self.response.set_status(400)
# 				self.response.write('Bad ID')
# 		else:
# 			self.response.write(json.dumps([d.to_dict() for d in Boat.query()]))
#
#
# 	# modify/edit boat (name, type, and/or length)
# 	# patch should not be used to modify at_sea
# 	def patch(self, id=None):
# 		if(not id):
# 			self.response.set_status(400)
# 			self.response.write('Require Boat ID')
#
# 		if(not IsExist(id)):
# 			self.response.set_status(400)
# 			self.response.write('Bad ID')
# 		else:
# 			update_data = json.loads(self.request.body)
# 			data = ndb.Key(urlsafe=id).get()
#
# 			if(update_data.get('name')):
# 				data.name = update_data['name']
# 			if(update_data.get('type')):
# 				data.type = update_data['type']
# 			if(update_data.get('length')):
# 				data.length = update_data['length']
#
# 			data.put()
#
# 			self.response.write(json.dumps(data.to_dict()))
#
#
# 	# delete boat
# 	def delete(self, id=None):
# 		if(not id):
# 			self.response.set_status(400)
# 			self.response.write('Require Boat ID')
#
# 		if(not IsExist(id)):
# 			self.response.set_status(400)
# 			self.response.write('Bad ID')
# 		else:
# 			data = ndb.Key(urlsafe=id).get()
#
# 			# if in slip, update slip data
# 			if(not data.at_sea):
# 				slip = Slip.query(Slip.current_boat == id).get()
# 				slip.current_boat = None
# 				slip.arrival_date = None
# 				slip.put()
#
# 			data.key.delete()
#
#
# class SlipHandler(webapp2.RequestHandler):
# 	# add a new slip
# 	def post(self):
# 		# user submits request with data for slip number
# 		data = json.loads(self.request.body)
# 		new_slip = Slip(number=data['number'], current_boat=None, arrival_date=None, departure_history=[])
#
# 		new_slip.put()
# 		new_slip.id = new_slip.key.urlsafe()
# 		new_slip.put()
#
# 		slip_dict = new_slip.to_dict()
#
# 		self.response.write(json.dumps(slip_dict))
#
#
# 	# get data for specific instance or list if id is not specified
# 	def get(self, id=None):
# 		if(id):
# 			if(not IsExist(id)):
# 				self.response.set_status(400)
# 				self.response.write('Bad ID')
# 			else:
# 				data = ndb.Key(urlsafe=id).get()
# 				self.response.write(json.dumps(data.to_dict()))
# 		else:
# 			self.response.write(json.dumps([d.to_dict() for d in Slip.query()]))
#
# 	# modify/edit slip
# 	# patch should not be used to modify boat or dates as those are relational information
# 	def patch(self, id=None):
# 		if(not id):
# 			self.response.set_status(400)
# 			self.response.write('Require Slip ID')
#
# 		if(not IsExist(id)):
# 			self.response.set_status(400)
# 			self.response.write('Bad ID')
# 		else:
# 			update_data = json.loads(self.request.body)
# 			data = ndb.Key(urlsafe=id).get()
#
# 			data.number = update_data['number']
# 			data.put()
#
# 			self.response.write(json.dumps(data.to_dict()))
#
#
# 	# delete slip
# 	def delete(self, id=None):
# 		if(not id):
# 			self.response.set_status(400)
# 			self.response.write('Require Slip ID')
#
# 		if(not IsExist(id)):
# 			self.response.set_status(400)
# 			self.response.write('Bad ID')
# 		else:
# 			data = ndb.Key(urlsafe=id).get()
#
# 			# if there's a boat update boat
# 			if(data.current_boat):
# 				boat = Boat.query(Boat.id == data.current_boat).get()
# 				boat.at_sea = True
# 				boat.put()
#
# 			data.key.delete()
#
#
#
# class SlipWithBoatHandler(webapp2.RequestHandler):
# 	# put a boat into a slip (body)
# 	def put(self, id=None):
# 		if(not id):
# 			self.response.set_status(400)
# 			self.response.write('Require Slip ID')
#
# 		if(not IsExist(id)):
# 			self.response.set_status(400)
# 			self.response.write('Bad Slip ID')
# 		else:
# 			put_boat_data = json.loads(self.request.body)
#
# 			if(not IsExist(put_boat_data['boat_id'])):
# 				self.response.set_status(400)
# 				self.response.write('Bad Boat ID')
# 			else:
# 				slip_data = ndb.Key(urlsafe=id).get()
#
# 				# returns 403 forbidden if slip is already occupied
# 				if(slip_data.current_boat):
# 					self.response.set_status(403)
# 					self.response.write('Error: Slip is occupied')
# 				else:
# 					boat_data = ndb.Key(urlsafe=put_boat_data['boat_id']).get()
#
# 					# update boat status in db
# 					boat_data.at_sea = False
# 					boat_data.put()
#
# 					# update slip data (boat id, arrival date)
# 					slip_data.current_boat = put_boat_data['boat_id']
# 					slip_data.arrival_date = put_boat_data['arrival_date']
# 					slip_data.put()
# 					self.response.write(json.dumps(slip_data.to_dict()))
#
#
# 	# get information on boat slip is holding, if any
# 	def get(self, id=None):
# 		if(not id):
# 			self.response.set_status(400)
# 			self.response.write('Require Slip ID')
#
# 		if(not IsExist(id)):
# 			self.response.set_status(400)
# 			self.response.write('Bad ID')
# 		else:
# 			slip_data = ndb.Key(urlsafe=id).get()
#
# 			if(not slip_data.current_boat):
# 				self.response.set_status(204)
# 			else:
# 				boat_data = ndb.Key(urlsafe=slip_data.current_boat).get()
# 				self.response.write(json.dumps(boat_data.to_dict()))
#
#
# 	# remove boat from slip
# 	def delete(self, id=None):
# 		if(not id):
# 			self.response.set_status(400)
# 			self.response.write('Require Slip ID')
#
# 		if(not IsExist(id)):
# 			self.response.set_status(400)
# 			self.response.write('Bad ID')
# 		else:
# 			slip_data = ndb.Key(urlsafe=id).get()
#
# 			if(not slip_data.current_boat):
# 				self.response.set_status(204)
# 			else:
# 				boat_data = ndb.Key(urlsafe=slip_data.current_boat).get()
#
# 				# record boat departure
# 				departure_data = DepartureHistory(
# 					departure_boat=slip_data.current_boat,
# 					departure_date=str(date.today()))
# 				slip_data.departure_history.append(departure_data)
#
# 				# update rest of slip
# 				slip_data.current_boat = None
# 				slip_data.arrival_date = None
# 				slip_data.put()
#
# 				# update boat data
# 				boat_data.at_sea = True
# 				boat_data.put()
#
# 				self.response.write(json.dumps(slip_data.to_dict()))


# debugging purposes only
class DeleteAll(webapp2.RequestHandler):
	def get(self):
		ndb.delete_multi(Account.query().fetch(keys_only=True))
		ndb.delete_multi(StockAsset.query().fetch(keys_only=True))
