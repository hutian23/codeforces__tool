import requests
from lxml import etree
import os
import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}

def login(handle, passwd):
    print('logining ...')
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
        print('login successfully')
        return Session
    else:
        raise Exception('不存在该用户/密码输出错误')

def getSource(Session, submissionId, filename):
    params = {
        'submissionId': submissionId,
    }
    post_url = 'https://codeforces.com/data/submitSource'
    response = Session.post(url=post_url, params=params)
    if response.status_code == 200:
        data = response.json()
        source = data['source']
        with open(filename, 'w', encoding='utf-8') as fp:
            fp.write(source)
            print(filename, '写入成功')
    else:
        raise Exception(
            '请求提交资源失败--->getSource(Session, submissionId,filename)')

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

def get_filename(contestId):
    Type_dic = {
        'C++': ['.cpp', 'C++'],
        'G++': ['.cpp', 'C++'],
        'Java': ['.java', 'Java'],
        'Python': ['.py', 'Python'],
        'PyPy': ['.py', 'Python'],
        'GCC': ['.c', 'C'],
        'C11': ['.c', 'C']
    }
    with open('./status/'+contestId+'.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        dic = data['result']
        filename_list = []
        for i in range(len(dic)):
            source = dic[i]['programmingLanguage']
            type = ''
            language = ''
            for j in Type_dic:
                if j in source:
                    type = Type_dic[j][0]
                    language = Type_dic[j][1]
                    verdict = dic[i]['verdict']
                    index = dic[i]['problem']['index']
                    handle = dic[i]['author']['members'][0]['handle']
                    filename = "%s__%s__%s__%s" % (
                        index, handle, language, verdict)+type
                    filename_list.append(filename)
    return filename_list

try:
    Session = login(sys.argv[1], sys.argv[2])
    contestId=sys.argv[3]
    submissionId_list = getId(contestId)
    filename_list = get_filename(contestId)
    if not os.path.exists('./code/'+contestId):
        os.makedirs('./code/'+contestId)
    if not os.path.exists('./TAR/'):
        os.mkdir('./TAR/')
    pool = ThreadPoolExecutor(max_workers=4)
    for i in range(len(submissionId_list)):
        pool.submit(getSource, Session,submissionId_list[i], './code/'+contestId+'/'+filename_list[i])
except Exception as e:
    print(e)
  
