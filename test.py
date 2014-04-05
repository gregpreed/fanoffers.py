import json
import urllib
import httplib
import pprint

HOST = 'localhost'
PORT = 8888
URL = '/auth/facebook'
args = {
    'access_token': 'CAACy91s5RDEBAJVKUP5xuABNp2BmlCSvwwPI1kWTMuZBfHov7PmB5BRyZBZCOufDR3Rcbndxlf9HZCzrWhLZBAEaXexzblCZC8zVxdUlZBQOIbrECpWR1KiaAnrH7ypeuiSqSyUfZCD2Q6jTpP8OX5ZA45WQvdBj5cEIVQRv8VUSKwXVrgEngyXuFf2JDC9FZC4j4ZD'
}
conn = httplib.HTTPConnection(HOST, PORT)
url = '%s?%s' % (URL, urllib.urlencode(args))
conn.request('GET', url)
response = conn.getresponse()
print response.status
print response.reason
print pprint.pprint(json.loads(response.read()))
