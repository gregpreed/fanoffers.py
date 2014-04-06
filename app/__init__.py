import os
from tornado.web import Application as BaseApplication
from neo4jrestclient.client import GraphDatabase
import app.controllers as c
import app.settings as s

location = lambda x: os.path.join(os.path.dirname(__file__), x)


class Application(BaseApplication):

    def __init__(self):
        handlers = (
            (r'/test', c.Test),
            (r'/auth/facebook', c.FacebookAuth),
        )
        db = '%s:%s%s' % (s.NEO4J_HOST, s.NEO4J_PORT, s.NEO4J_DB)
        self.db = GraphDatabase(db)
        settings = {'debug': s.DEBUG,
                    'cookie_secret': s.COOKIE_SECRET,
                    'facebook_api_key': s.FACEBOOK_API_KEY,
                    'facebook_secret': s.FACEBOOK_SECRET,
                    'twitter_api_key': s.TWITTER_API_KEY,
                    'twitter_secret': s.TWITTER_SECRET}
        super(Application, self).__init__(handlers, **settings)
