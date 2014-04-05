import json
from tornado.web import RequestHandler


class Test(RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'application/json')
        return self.finish(json.dumps({'response': 'Hello world!'}))

from app.controllers.auth import *
