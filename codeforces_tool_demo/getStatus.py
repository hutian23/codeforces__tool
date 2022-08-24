import requests
import json
from fetchAPI import *
import sys
import os
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}


def getStatus(action, action_param, apiKey, apiSecret):
    url = get_API(action, action_param, apiKey, apiSecret)
    print('sending a HTTP-request to address:<a href="%s" target="_blank">API的url</a>'%url)
    response = requests.get(url=url, headers=headers)
    path = 'status'
    status_json = path+'/'+action_param['contestId']+'.json'
    if response.status_code == 403:
       with open(status_json, 'w', encoding='utf-8') as f:
            data = {
                'status': 'FAILED',
                'comment': '403,API is not available temporary'
            }
            json.dump(data, f)
    elif response.status_code == 200:
        data = response.json()
        with open(status_json, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    else:
        data = response.json()
        with open(status_json, 'w', encoding='utf-8') as f:
            json.dump(data, f)

action_param = {
    'contestId': sys.argv[2]
}
if not os.path.exists('./status/'):
    os.makedirs('./status/')

getStatus(sys.argv[1], action_param, sys.argv[3], sys.argv[4])