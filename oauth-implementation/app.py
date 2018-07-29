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

# assume API is enabled on console.developers.google.com/apis
# use Google+ API to get user's own profile data

# for prod:
CLIENT_ID = "1011393638628-nqqof6v98h9pu2rnlpimdcnhit63lcih.apps.googleusercontent.com"
CLIENT_SECRET = "bs150y1S76z8K4FCG8SKFKIS"
REDIRECT_URI = "https://axial-paratext-210920.appspot.com/oauth"

# for debugging
# CLIENT_ID = "1011393638628-tbdi415g5vir3fsbj0ojjudrvp8avlmt.apps.googleusercontent.com"
# CLIENT_SECRET = "Nq_dWz17NFrK7dXtKZyaLjX-"
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
			path = os.path.join(os.path.dirname(__file__), 'html/reject.html')
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
			first_name = results['name']['givenName']
			last_name = results['name']['familyName']
			gplus_link = results['url']

			template_values = {
				'fname': first_name,
				'lname': last_name,
				'gplink': gplus_link,
				'state': state,
				'url': "/"
			}
			path = os.path.join(os.path.dirname(__file__), 'html/oauth.html')
			self.response.out.write(template.render(path, template_values))


# # [START app]
# allowed_methods = webapp2.WSGIApplication.allowed_methods
# new_allowed_methods = allowed_methods.union(('PATCH',))
# webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/oauth', OAuthHandler)
], debug=True)
# [END app]