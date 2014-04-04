import os
from tornado.web import Application as BaseApplication
import fanoffers.app.controllers as c


location = lambda x: os.path.join(os.path.dirname(__file__), x)

class Application(BaseApplication):

    def __init__(self):
        handlers = (
            (r'/test', c.Test),
        )
        settings = {'debug': True}
        super(Application, self).__init__(handlers, **settings)
