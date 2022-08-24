import json
import requests
from lxml import etree
import hashlib
import time
import random

def getRandomString():
    str = ""
    for i in range(6):
        ch = chr(random.randrange(ord('0'), ord('9')+1))
        str += ch
    return str


def get_API(action, action_param, apiKey, apiSecret, time=int(time.time()), apiSig=getRandomString()):
    base_url = 'https://codeforces.com/api/'
    str1 = ""
    for i in action_param:
        str1 += "%s=%s&" % (i, action_param[i])
    str2 = "%s/%sapiKey=%s&%stime=%d#%s" % (apiSig,action, apiKey, str1, time, apiSecret)
    hash = hashlib.sha512(str2.encode('utf-8')).hexdigest()
    url = base_url + "%s%sapiKey=%s&time=%s&apiSig=%s" % (action, str1, apiKey, time, apiSig) + hash
    return url
