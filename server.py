import os
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from app import Application

location = lambda x: os.path.join(os.path.dirname(__file__), x)

define('port', default=8000, type=int)

if __name__ == '__main__':
    parse_command_line()
    http_server = HTTPServer(Application())
    http_server.listen(options.port)
    print 'Running @ %s' % options.port
    IOLoop.instance().start()
