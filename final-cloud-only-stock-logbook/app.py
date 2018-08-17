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
from handler import AccountHandler, StockAssetHandler, ShowStockAssetHandler, DeleteAll


CLIENT_ID = "239082154858-bm4h8a9dm1au1d6pom1oovqijsfp28ed.apps.googleusercontent.com"
CLIENT_SECRET = "47gQnq0QGbcySIOa9bPvx85q"
REDIRECT_URI = "https://cs396-final-vaca-1533865861093.appspot.com/oauth"
# REDIRECT_URI = "http://localhost:8080/oauth"

SCOPE = "email"

TOKEN_URL="https://www.googleapis.com/oauth2/v4/token"
RETRIEVE_DATA_URL="https://www.googleapis.com/plus/v1/people/me"


# main page - user clicks to request client to initiate auth
class MainPage(webapp2.RequestHandler):
	def get(self):
		# generate state
		state = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

		# create url to send user to google auth endpoint directly
		url = ("https://accounts.google.com/o/oauth2/v2/auth?"
			+ "client_id=" + CLIENT_ID
			+ "&redirect_uri=" + REDIRECT_URI
			+ "&scope=" + SCOPE
			+ "&state=" + state
			+ "&response_type=code"
			+ "&prompt=consent"
			+ "&include_granted_scopes=true")

		# rendering and serving the html template page
		path = os.path.join(os.path.dirname(__file__), 'html/main_page.html')
		self.response.out.write(template.render(path, {'url': url}))

# Redirect after user gives server OK
class OAuthHandler(webapp2.RequestHandler):
	def get(self):
		# user rejects to give permission or some other error
		if(self.request.get('error')):

			# setup another link to authenticate again
			state = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])
			url = ("https://accounts.google.com/o/oauth2/v2/auth?"
			+ "client_id=" + CLIENT_ID
			+ "&redirect_uri=" + REDIRECT_URI
			+ "&scope=" + SCOPE
			+ "&state=" + state
			+ "&response_type=code"
			+ "&prompt=consent"
			+ "&include_granted_scopes=true")
			path = os.path.join(os.path.dirname(__file__), 'html/main_page.html')
			self.response.out.write(template.render(path, {'url': url}))

		else:
			# retrieve response from server
			state = self.request.GET['state']
			auth_code = self.request.GET['code']

			# POST to server with received info for token
			header = {'Content-Type':'application/x-www-form-urlencoded'}
			body = {
				'code':auth_code,
				'client_id': CLIENT_ID,
				'client_secret': CLIENT_SECRET,
				'redirect_uri': REDIRECT_URI,
				'grant_type': 'authorization_code'
			}

			results = urlfetch.fetch(
				url=TOKEN_URL,
				payload=urllib.urlencode(body),
				method=urlfetch.POST,
				headers=header
				)

			# Use fetched token to get user data
			access_token = json.loads(results.content)['access_token']

			header = {'Authorization': 'Bearer ' + access_token}
			results = urlfetch.fetch(
				url=RETRIEVE_DATA_URL,
				method=urlfetch.GET,
				headers=header
				)

			# Process retrieved data
			results = json.loads(results.content)

			name = results['displayName']
			user_id = str(results['id'])
			email = results['emails'][0]['value']
			occupation = ''
			if 'occupation' in results:
				occupation = results['occupation']
			else:
				occupation = "N/A"

			# Check if user already in DB, if not, create an instance
			is_user_new = True
			user_account = None
			for user in Account.query():
				if user.user_id == user_id:
					is_user_new = False
					user_account = user

			welcome_message = "Welcome Back! Please ensure you are using the latest token."
			if is_user_new == True:
				welcome_message = "Welcome! Please use the token below to use our APIs."

				# Create new instance for user - their "account"
				new_user_account = Account(occupation=occupation,
					name=name,
					email=email,
					asset_count=0,
					user_id=user_id,
					id=user_id)
				new_user_account.put()
				user_account = new_user_account

			# Load values to display on front-end
			template_values = {
				'name': user_account.name,
				'user_id': user_account.user_id,
				'email': user_account.email,
				'occupation': user_account.occupation,
				'access_token': access_token,
				'welcome_message': welcome_message,
				'url': "/"
			}
			path = os.path.join(os.path.dirname(__file__), 'html/oauth.html')
			self.response.out.write(template.render(path, template_values))


# [START app]
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/oauth', OAuthHandler),
	('/user/(.*)', AccountHandler),
	('/stock/(.*)', StockAssetHandler),
	('/stocks/me', ShowStockAssetHandler),
	('/deleteall', DeleteAll) # DEBUGGING ONLY!
], debug=True)
# [END app]
