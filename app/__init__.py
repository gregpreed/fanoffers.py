import os
from tornado.web import Application as BaseApplication
import app.controllers as c
import app.settings as s

location = lambda x: os.path.join(os.path.dirname(__file__), x)


class Application(BaseApplication):

    def __init__(self):
        handlers = (
            (r'/test', c.Test),
            (r'/auth/facebook', c.FacebookAuth),
        )
        settings = {'debug': s.DEBUG,
                    'cookie_secret': s.COOKIE_SECRET,
                    'facebook_api_key': s.FACEBOOK_API_KEY,
                    'facebook_secret': s.FACEBOOK_SECRET,
                    'twitter_api_key': s.TWITTER_API_KEY,
                    'twitter_secret': s.TWITTER_SECRET}
        super(Application, self).__init__(handlers, **settings)
