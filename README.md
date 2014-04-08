#FanOffers python backend

##Requirements
  - openjdk==7
  - neo4j==2.0.1
  - virtualenv
  - redis

##Installation
	$ git clone git@github.com:gregpreed/fanoffers.py.git
	$ mv fanoffers.py fanoffers
	$ cd fanoffers
	$ virtualenv venv --no-site-packages
	$ venv/bin/pip install -r requirements.txt

##Configuration
###settings.py

	DEGUB = {True, False}
	NEO4J_HOST = {eg http://localhost}
	NEO4J_PORT = {eg 7474}
	NEO4J_DB = {eg /db/data/}
	FACEBOOK_API_KEY = {facebook_api_key}
	FACEBOOK_SECRET = {facebook_secret}
	TWITTER_CONSUMER_KEY = {twitter_consumer_key}
	TWITTER_CONSUMER_SECRET = {twitter_comsumer_secret}
	CELERY_BROKER_URL = {eg redis://localhost:6379}
	CELERY_RESULT_BACKEND = {eg redis://localhost:6379/0}
	
Example generate cookie secret (python):

	import base64
	import uuid
	print base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

##Use
###Neo4j database
	$ sudo service neo4j start
###Python REST server
(Set up with a process monitor-control system in production - eg: supervisord)

	$ venv/bin/python server.py --port={port_number}
###Redis server
	$ sudo service redis_{port} start
###Celery task queue
(Set up with a process monitor-control system in production - eg: supervisord)

	$ venv/bin/celery -A app.controllers.process worker

##Endpoints
###Process
####/process/facebook

	POST
	
	{
		id,
		friend_list,
		like_list
	}
	
	RESPONSE
	
	204
	
####/process/twitter

	POST
	
	{
		id,
		follower_list,
		following_list
	}
	
	RESPONSE
	
	204	
	
	
##Neo4j
###Naming conventions
  - Labels: CamelCasedNames
  - Relationships: underscored_names
  - Property keys: underscored_names
  
###Labels
  - User
  - TwitterUser
  - FacebookUser
  
###Relationships
  - friend
  - follows
  - likes