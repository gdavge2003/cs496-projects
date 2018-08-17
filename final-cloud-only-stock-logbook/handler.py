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
STOCK_API_KEY="MDR1GHTMDRRDWBY2"


# helper function
# checks whether user id is in db or not
def UserExists(user_id):
	is_found = False
	for user in Account.query():
		if user.user_id == user_id:
			logging.info("User found!")
			is_found = True
			break

	return is_found


# checks whether user has stock asset
def UserHasStockAsset(user_id, symbol):
	stock = None
	for stockasset in StockAsset.query():
		if stockasset.user_id == user_id and stockasset.symbol == symbol:
			stock = stockasset

	return stock


# grabs the bearer token from user's auth header
def GetBearerToken(headers):
	logging.info(headers)
	if 'Authorization' in headers:
		return headers['Authorization'].split()[1]
	else:
		return ''


# take token and checks with Google auth if valid token
def IsAuthorized(token, user_id):
	header = {'Authorization': 'Bearer ' + token}
	results = urlfetch.fetch(
		url=RETRIEVE_DATA_URL,
		method=urlfetch.GET,
		headers=header
		)

	results = json.loads(results.content)
	check = None if 'error' in results else results['id']

	if check == None:
		logging.info("Bad token used for authorization")
		return False
	elif check != user_id:
		logging.info("Successful authorization but not authorized to edit acc")
		return False
	else:
		logging.info("Successful token authorization!")
		return True


# gets user_id given valid token
def GetUserId(token):
	header = {'Authorization': 'Bearer ' + token}
	results = urlfetch.fetch(
		url=RETRIEVE_DATA_URL,
		method=urlfetch.GET,
		headers=header
		)

	results = json.loads(results.content)
	check = None if 'error' in results else results['id']

	if check == None:
		logging.info("Bad token used for authorization")
	return check


# fetch the requested stock. returns array of [price, last updated]
def GetStockInfo(symbol):
	result_string = ("https://www.alphavantage.co/query?" +
	"function=TIME_SERIES_DAILY" +
	"&symbol=" + symbol +
	"&outputsize=compact" +
	"&apikey=" + STOCK_API_KEY)

	logging.info("Fetching... " + result_string)
	# results = urlfetch.fetch(
	# 	url=result_string,
	# 	method=urlfetch.GET,
	# 	headers={'Content-Type':'application/x-www-form-urlencoded'}
	# 	)
	results = urlfetch.fetch(result_string)
	logging.info("Fetched raw data:")
	logging.info(results)

	json_results = json.loads(results.content)
	results_dict = {}
	if 'Meta Data' in json_results:
		logging.info("Stock fetched successfully: " + symbol)
		last_updated = json_results['Meta Data']['3. Last Refreshed'].split()[0]
		results_dict['last_updated'] = last_updated
		results_dict['price'] = json_results['Time Series (Daily)'][last_updated]['1. open']
	else:
		logging.info("Bad json fetched or failed")
		results_dict = None

	return results_dict


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
			if not IsAuthorized(token, user_id):
				self.response.status = 401
				self.response.write("Error: Invalid authentication token or not allowed to modify.")
			else:
				# passed authentication. correct parameter. use body to modify
				data = Account.get_by_id(user_id)
				update_data = json.loads(self.request.body) # convert string to json obj

				for key in update_data:
					# if key exists in account data, update it
					if key == 'name':
						data.name = update_data[key]
					elif key == 'occupation':
						data.occupation = update_data[key]
					elif key == 'email':
						data.email = update_data[key]

				data.put()

				# send out updated information
				self.response.write(data.to_dict())


	# deletes user account - removes all associated stock assets as well
	def delete(self, user_id=None):
		if not user_id:
			self.response.status = 400
			self.response.write("Error: User_id must be specified in request.")
		elif not UserExists(user_id):
			self.response.status = 404
			self.response.write("Error: User does not exist in database.")
		else:
			# check correct token for identity. user cannot delete other users' accounts
			token = GetBearerToken(self.request.headers)
			if not IsAuthorized(token, user_id):
				self.response.status = 401
				self.response.write("Error: Invalid authentication token or not allowed to delete.")
			else:
				data = Account.get_by_id(user_id)
				data.key.delete()

				# delete account's associated assets
				for stockasset in StockAsset.query():
					if stockasset.user_id == user_id:
						stockasset.key.delete()

class StockAssetHandler(webapp2.RequestHandler):
	# gets basic information for stock
	def get(self, stock_symbol=None):
		if not stock_symbol:
			self.response.status = 400
			self.response.write("Error: Stock symbol must be specified in request.")
		else:
			results = GetStockInfo(stock_symbol)

			# check if valid symbol used
			if results is None:
				self.response.status = 404
				self.response.write("Error: Stock doesn't exist. Check Symbol.")
			else:
				data = {
					'symbol': stock_symbol,
					'price_usd_open': results['price'],
					'last_updated': results['last_updated']
				}

				self.response.write(json.dumps(data))

	# create a new stock asset for user
	def post(self, stock_symbol=None):
		# get data
		stock_data = GetStockInfo(stock_symbol)
		logging.info(stock_data) # adding this to debug weird postman behavior
		token = GetBearerToken(self.request.headers)
		user_id = GetUserId(token)
		user_req = json.loads(self.request.body)

		# check valid user
		if user_id == None:
			self.response.status = 401
			self.response.write("Error: Invalid token, unable to authenticate.")
		# no stock symbol mentioned in request
		elif not stock_symbol:
			self.response.status = 400
			self.response.write("Error: Stock symbol must be specified in request.")
		# check valid stock
		elif stock_data is None:
			self.response.status = 404
			self.response.write("Error: Stock doesn't exist. Check Symbol.")
		# check correct body attribute
		elif 'owned_count' not in user_req:
			self.response.status = 400
			self.response.write("Error: POST body is missing 'owned_count' value.")
		# check if user already has this asset
		elif UserHasStockAsset(user_id, stock_symbol) is not None:
			self.response.status = 400
			self.response.write("Error: You already own this stock." +
				"Please use PATCH instead to modify amount or PUT to add amount.")
		else:
			stock = StockAsset(
				user_id=user_id,
				symbol=stock_symbol,
				owned_count=user_req['owned_count'],
				price_usd_open=stock_data['price'],
				last_updated=stock_data['last_updated']
				)
			stock.put()
			stock.id = stock.key.urlsafe()
			stock.put()

			account = Account.get_by_id(user_id)
			account.asset_count = account.asset_count + 1
			account.put()

			self.response.write(json.dumps(stock.to_dict()))

	# modify user's current stock assset
	def patch(self, stock_symbol=None):
		# get data
		stock_data = GetStockInfo(stock_symbol)
		token = GetBearerToken(self.request.headers)
		user_id = GetUserId(token)
		user_req = json.loads(self.request.body)
		user_stock_data = UserHasStockAsset(user_id, stock_symbol)

		# check valid user
		if user_id == None:
			self.response.status = 401
			self.response.write("Error: Invalid token, unable to authenticate.")
		# no stock symbol mentioned in request
		elif not stock_symbol:
			self.response.status = 400
			self.response.write("Error: Stock symbol must be specified in request.")
		# check valid stock
		elif stock_data is None:
			self.response.status = 404
			self.response.write("Error: Stock doesn't exist. Check Symbol.")
		# check correct body attribute
		elif 'owned_count' not in user_req:
			self.response.status = 400
			self.response.write("Error: PATCH body is missing 'owned_count' value.")
		# check if user already has this asset
		elif user_stock_data is None:
			self.response.status = 400
			self.response.write("Error: User does not own this stock and hence" +
				" it cannot be modified. Please use POST if adding new asset.")
		else:
			# update amount, and update other stats from stock server
			user_stock_data.owned_count = user_req['owned_count']
			user_stock_data.last_updated = stock_data['last_updated']
			user_stock_data.price_usd_open = stock_data['price']

			user_stock_data.put()

			self.response.write(json.dumps(user_stock_data.to_dict()))

	# add stock amount to existing amount
	def put(self, stock_symbol=None):
		# get data
		stock_data = GetStockInfo(stock_symbol)
		token = GetBearerToken(self.request.headers)
		user_id = GetUserId(token)
		user_req = json.loads(self.request.body)
		user_stock_data = UserHasStockAsset(user_id, stock_symbol)

		# check valid user
		if user_id == None:
			self.response.status = 401
			self.response.write("Error: Invalid token, unable to authenticate.")
		# no stock symbol mentioned in request
		elif not stock_symbol:
			self.response.status = 400
			self.response.write("Error: Stock symbol must be specified in request.")
		# check valid stock
		elif stock_data is None:
			self.response.status = 404
			self.response.write("Error: Stock doesn't exist. Check Symbol.")
		# check correct body attribute
		elif 'owned_count' not in user_req:
			self.response.status = 400
			self.response.write("Error: PUT body is missing 'owned_count' value.")
		# check if user already has this asset
		elif user_stock_data is None:
			self.response.status = 400
			self.response.write("Error: User does not own this stock and hence" +
				" it cannot be added to. Please use POST if adding new asset.")
		else:
			# update amount, and update other stats from stock server
			user_stock_data.owned_count = user_stock_data.owned_count + user_req['owned_count']
			user_stock_data.last_updated = stock_data['last_updated']
			user_stock_data.price_usd_open = stock_data['price']

			user_stock_data.put()

			self.response.write(json.dumps(user_stock_data.to_dict()))

	# deletes stock instance from user account
	def delete(self, stock_symbol=None):
		# get data
		token = GetBearerToken(self.request.headers)
		user_id = GetUserId(token)
		user_stock_data = UserHasStockAsset(user_id, stock_symbol)

		# check valid user
		if user_id == None:
			self.response.status = 401
			self.response.write("Error: Invalid token, unable to authenticate.")
		# no stock symbol mentioned in request
		elif not stock_symbol:
			self.response.status = 400
			self.response.write("Error: Stock symbol must be specified in request.")
		# check if user already has this asset
		elif user_stock_data is None:
			self.response.status = 400
			self.response.write("Error: User does not own this stock and hence" +
				" it cannot be deleted.")
		else:
			# delete instance, and decrement user asset by 1
			user_stock_data.key.delete()

			account = Account.get_by_id(user_id)
			account.asset_count = account.asset_count - 1
			account.put()

			self.response.write(json.dumps(account.to_dict()))


class ShowStockAssetHandler(webapp2.RequestHandler):
	# gets list of stock assets user owns
	def get(self):
		# get data
		token = GetBearerToken(self.request.headers)
		user_id = GetUserId(token)

		# check valid user
		if user_id == None:
			self.response.status = 401
			self.response.write("Error: Invalid token, unable to authenticate.")
		else:
			stocks_owned = {}

			for stockasset in StockAsset.query():
				if stockasset.user_id == user_id:
					stocks_owned[stockasset.symbol] = stockasset.to_dict()

			self.response.write(json.dumps(stocks_owned))


# debugging purposes only
class DeleteAll(webapp2.RequestHandler):
	def get(self):
		ndb.delete_multi(Account.query().fetch(keys_only=True))
		ndb.delete_multi(StockAsset.query().fetch(keys_only=True))
