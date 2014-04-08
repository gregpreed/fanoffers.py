import json
from tornado.web import RequestHandler


class Test(RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'application/json')
        return self.finish(json.dumps({'response': 'Hello world!'}))


class Controller(RequestHandler):

    def json_write(self, chunk):
        self.set_header('Content-Type', 'application/json')
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk)
        self.write(chunk)

from app.controllers.auth import *
from app.controllers.process import *
