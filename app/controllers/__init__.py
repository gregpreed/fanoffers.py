import json
from tornado.web import RequestHandler


class Test(RequestHandler):

    def get(self):
        return self.finish(json.dumps({'response': 'Hello world!'}))
