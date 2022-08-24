import requests
from lxml import etree
import json
import sys
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}

def login(handle, passwd):
    print('pre-logining ...')
    url = 'https://codeforces.com/enter?'
    Session = requests.session()
    response = Session.get(url=url, headers=headers)
    tree = etree.HTML(response.text)
    csrf_token = tree.xpath('//meta[@name="X-Csrf-Token"]/@content')[0]
    param = {
        'csrf_token': csrf_token,
        'action': 'enter',
        'handleOrEmail': handle,
        'password': passwd
    }
    response = Session.post(url=url, params=param, headers=headers)
    s = False
    for i in Session.cookies.items():
        for j in i:
            if j == 'X-User-Sha1':
                s = True
    if(s):
        print('pre-login successfully')
        return Session
    else:
        raise Exception('不存在该用户/密码输出错误')

def getId(contestId):
    id_list = []
    with open('./status/'+contestId+'.json', 'r') as f:
        data = json.load(f)
        _list = data['result']
        if len(_list) == 0:
            raise Exception('没有可以解析的数据--->getId()')
        for i in range(len(_list)):
            id_list.append(_list[i]['id'])
    return id_list

try:
    handle = sys.argv[1]
    password = sys.argv[2]
    contestId = sys.argv[3]
    login(handle, password)
    submissionId_list = getId(contestId)
    with open('./status/'+contestId+'_source.json', 'w') as f:
        data = {
            'status': 'OK',
            'length': len(submissionId_list),
            'comment': '',
            'handle': handle,
            'password': password
        }
        json.dump(data, f)
except Exception as e:
    with open('./status/'+contestId+'_source.json', 'w', encoding='utf-8') as f:
        data = {
            'status': 'FAILED',
            'length': 0,
            'comment': e.args[0],
            'handle': handle,
            'password': password
        }
        print(data)
        json.dump(data, f, ensure_ascii=False)
