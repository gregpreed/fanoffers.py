from tornado.web import RequestHandler


class Test(RequestHandler):

    def get(self):
        return self.write('Hello world!')
