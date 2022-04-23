import requests
import json
import datetime
from dateutil.relativedelta import relativedelta
import time

with open('./keys/stack.txt', 'r') as f:
    TOKEN = f.read()

SITE = 'stackoverflow'
TAGS = 'python'

d = datetime.datetime.now() - relativedelta(months=1)
unixtime = time.mktime(d.timetuple())

qry = 'https://api.stackexchange.com/2.3/questions?order=desc&sort=votes&tagged=' + TAGS +'&pagesize=100&fromdate=' + str(int(unixtime)) + "&site=" + SITE + '&key=' + TOKEN
response = requests.get(qry)
response = response.json()

# print(unixtime)
# print(response)
for r in response['items']:
    if (r['is_answered']):
        print(r['link'], r['score'])