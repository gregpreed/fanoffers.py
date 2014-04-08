import json
import urllib
import httplib
import pprint

HOST = 'localhost'
PORT = 8001
URL = '/process/facebook'
conn = httplib.HTTPConnection(HOST, PORT)
body = {'friend_list': [{'name': 'alice'}, {'name': 'bob'}],
        'like_list': [{'id': '1', 'name': 'spice girls'}],}
conn.request('POST', URL, json.dumps(body))
response = conn.getresponse()
print response.status
print response.reason
# print pprint.pprint(json.loads(response.read()))
