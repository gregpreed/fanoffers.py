#FanOffers python backend

##Requirements
  - neo4j
  - virtualenv

##Installation
	$ git clone git@github.com:gregpreed/fanoffers.py.git
	$ mv fanoffers.py fanoffers
	$ cd fanoffers
	$ virtualenv venv --no-site-packages
	$ venv/bin/pip install -r requirements.txt

##Configuration
###settings.py

	DEGUB = {True, False}
	COOKIE_SECRET = {long random sequences of bits}
	FACEBOOK_API_KEY = {your api key}
	FACEBOOK_SECRET = {your secret}
	TWITTER_API_KEY = {your api_key}
	TWITTER_SECRET = {your secret}	
	
Example generate cookie secret (python):

	import base64
	import uuid
	print base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

##Endpoints
###Auth
####/auth/facebook

	GET
	
	{
		access_token *,
		expires
	}
	
	RESPONSE
	
	200
	{
		item: {
			id,
			name,
			email,
			image
		}
	}
	
	400 - Code missed or invalid