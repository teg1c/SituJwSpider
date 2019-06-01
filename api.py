# -*- coding:utf-8 -*-
import time
import requests
import json
from lxml import html
from crypto_rsa.base64 import Base64 as pB64
from crypto_rsa.RSAJS import RSAKey
from flask import Flask, abort, request, jsonify
import codecs
import sys
import re
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
app = Flask(__name__)
app.config.update(DEBUG=True)
class Core(object):
    baseUrl = "http://218.61.108.169/jwglxt"
    ntime = int(time.time())
    indexUrl = baseUrl + "/xtgl/login_slogin.html?language=zh_CN&_t={}".format(ntime)
    publicKeyUrl = baseUrl + "/xtgl/login_getPublicKey.html?time={}&_={}".format(ntime, ntime - 10)
    headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-ncoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': '218.61.108.169',
            'Pragma': 'no-cache',
            'Upgrad-Insecure-Requests': '1',
            'Referer': indexUrl,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/72.0.3626.119 Safari/537.36',
        }
    time_now = int(time.time())
    
    def __init__(self, account="", passwd=""):
        self.account = account
        self.password = passwd
        self.loginStatus = False
        self.client = requests.session()

    def setLoginInfo(self, account, passwd):
        self.account = account
        self.password = passwd

    def __getEnPassword(self, string, exponent, modulus):
        b64 = pB64()
        exponent = b64.b64_to_hex(exponent)
        modulus = b64.b64_to_hex(modulus)
        rsa = RSAKey()
        rsa.setPublic(modulus, exponent)
        crypto_t = rsa.encrypt(string)
        return b64.hex_to_b64(crypto_t)

    def login(self):
        if self.account is "" or self.password is "":
            abort(500,'用户名密码不能为空')

        print(self.indexUrl)
        print(self.publicKeyUrl)
        try:
            bodyByGet = self.client.get(self.indexUrl,timeout=5)
            modExp = self.client.get(self.publicKeyUrl,timeout=5).json()
        except requests.exceptions.ConnectionError as e:
            abort(500,str(e))
        except requests.exceptions.ChunkedEncodingError as e:
            abort(500,str(e))
        except:
            abort(500,'错误')

        tree = html.fromstring(bodyByGet.text)
        csrftoken = tree.xpath('//*[@id="csrftoken"]/@value')

        data = [
            ('csrftoken', csrftoken),
            ('yhm', self.account),
            ('mm', self.__getEnPassword(self.password, modExp["exponent"], modExp["modulus"])),
            ('mm', self.__getEnPassword(self.password, modExp["exponent"], modExp["modulus"]))
        ]
        try:
            response = self.client.post(self.baseUrl + "/xtgl/login_slogin.html",
                                        headers=self.headers,
                                        data=data,
                                        timeout=5
                                        )
        except requests.exceptions.ConnectionError as e:
            abort(500,str(e))
        except requests.exceptions.ChunkedEncodingError as e:
            abort(500,str(e))
        except:
            abort(500,'错误')

        if "用户名或密码不正确，请重新输入" in response.text:
            abort(400,'密码错误')
            print("登录状态:登录失败")
            raise NameError("Login failed")

        else:
            self.loginStatus = True
            # data = self.getScore()
            print("success")
            # print("欢迎您：{} 同学".format(self.stuName))
            # print("专业:{}".format(self.stuMajor))
            return self.client

    def getStudentInfo(self):
            root_pattern = '<div class="form-group" >([\s\S]*?)</div>'
            itemNameCN_pattern = '<label class="col-sm-4 control-label" for="" >([\s\S]*?)</label>'
            itemVal_pattern = '<p class="form-control-static">([\s\S]*?)</p>'
            itemNameEN_pattren = '<div class="col-sm-8" id="([\s\S]*?)">'
            url = self.baseUrl + '/xsxxxggl/xsgrxxwh_cxXsgrxx.html?gnmkdm=N100801&layout=default&su=' + str(
                self.account)
            res = self.client.get(url, headers=self.headers)
            root_html = re.findall(root_pattern, res.text)
            anchors = []
            for html in root_html:
                itemNameCN = re.findall(itemNameCN_pattern, html)
                itemVal = re.findall(itemVal_pattern, html)
                itemNameEN = re.findall(itemNameEN_pattren, html)
                if not itemNameCN:
                    break
                anchor = {'itemNameCN': itemNameCN, 'itemVal': itemVal, 'itemNameEN': itemNameEN}
                anchors.append(anchor)
            l = lambda x: {
                'itemNameCN': x['itemNameCN'][0].strip().rstrip("："),
                'itemVal': x['itemVal'][0].strip(),
                'itemNameEN': x['itemNameEN'][0].strip().replace("col_", "")
            }
            resList = '{'
            for i, item in enumerate(list(map(l, anchors))):
                if i == len(list(map(l, anchors))) - 1:
                    resList = resList + '"' + item["itemNameEN"] + '":"' + item["itemVal"] + '"'
                else:
                    resList = resList + '"' + item["itemNameEN"] + '":"' + item["itemVal"] + '",'
            resList = resList + '}'

            return {'status': 1, 'msg': '成功！', 'data': json.loads(resList)}

    def getScore(self,xnm,xqm):
        params = (
            ('xnm', ''),
            ('xqm', ''),
            ('_search', 'false'),
            ('nd', format(self.ntime)),
            ('queryModel.showCount', 300),
            ('queryModel.currentPage', 1),
            ('queryModel.sortName', ''),
            ('queryModel.sortOrder', 'desc'),
            ('time', 0),
        )
        response = self.client.post(self.baseUrl + "/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005",
                                   params=params,
                                   timeout=5
                                   )
        res =  response.json()
        # for i, item in list(enumerate(res['items'])):
        #     responList = self.getScoreDetail(xnm, xqm, res['items'][i]['kcmc'], res['items'][i]['jxb_id'])
        #     res['items'][i]['details'] = responList
        if res["totalCount"] == 0:
            return {'status': 0, 'msg': '暂无数据！', 'data': res}
        else:
            return {'status': 1, 'msg': '获取成绩成功！', 'data': res}

    def getScoreDetail(self, xnm, xqm, kcmc, jxd_id):
        td_pattern = '<td valign="middle">([\s\S]*?)</td>'
        anchors_details=[]
        url = self.baseUrl + 'cjcx/cjcx_cxCjxq.html?time=' + str(self.time_now) + '&gnmkdm=N305005'
        data = {
            'jxb_id': jxd_id,
            'xnm': xnm,
            'xqm': xqm,
            'kcmc': kcmc
        }
        res = self.client.post(url, data=data, headers=self.headers)
        item_html = re.findall(td_pattern, res.text)
        for i, lession_info_item in enumerate(item_html):
            if i % 3 == 0:
                gradesItem = item_html[i]
                gradesPercent = item_html[i + 1]
                gradesScore = item_html[i + 2]
                anchor = {'gradesItem': gradesItem, 'gradesPercent': gradesPercent,'gradesScore': gradesScore}
                anchors_details.append(anchor)

        details_lambda = lambda x: {
                'gradesItem': x['gradesItem'].strip().rstrip(" 】").lstrip("【 "),
                'gradesPercent': x['gradesPercent'].strip().rstrip("&nbsp;"),
                'gradesScore': x['gradesScore'].strip().rstrip("&nbsp;"),
        }
        return list(map(details_lambda, anchors_details))


    def getTable(self, year = '2018', semester='12'):
        if self.loginStatus is not True:
            abort(400,'请登录')

        classTableUrl = self.baseUrl + "/kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151"
        # xnm 所选学年  2017 就是 2017-2018, 2016 就是2016-2017
        # xqm 所需学期  3 是第一学期，12 是第二学期
        data = [
            ("xnm", year),
            ("xqm", semester)
        ]
        try:
            result = self.client.post(classTableUrl,
                                   data=data,
                                   timeout=5
                                   ).json()
        except requests.exceptions.ConnectionError as e:
            abort(500,str(e))
        except requests.exceptions.ChunkedEncodingError as e:
            abort(500,str(e))
        except:
            abort(500,'错误')
        format = [];
        other = [];
        for each in result["kbList"]:
            # res = [
            #     'test':each["xqjmc"],each["jc"],each["cdmc"],each["zcd"],each["kcmc"])
            # ]
            res = [
                each["xqjmc"],each["jc"],each["cdmc"],each["zcd"],each["kcmc"]
            ]
            format.append(res)

        for each in result["sjkList"]:
            res = [
                '--',each["qsjsz"],'','',each["kcmc"]
            ]
            other.append(res)

        if format:
            return {'status':1,'msg':'success','data':format,'other':other}
        else:
            return {'status':0,'msg':'无数据'}

@app.route('/user/', methods=['GET','POST'])

def user():
    if request.method == 'GET':
        usename = request.args['username']
        password = request.args['password']
    else:
        usename = request.form['username']
        password = request.form['password']
    xnm = request.args.get('xnm','2018')
    xqm = request.args.get('xqm','12')
    client = Core(usename, password)
    # client = Core("17061211", "aixiao74525.")
    client.login()
    data = client.getStudentInfo()
    return jsonify(data)

@app.route('/table/', methods=['GET','POST'])

def table():
    if request.method == 'GET':
        usename = request.args['username']
        password = request.args['password']
    else:
        usename = request.form['username']
        password = request.form['password']
    xnm = request.args.get('xnm','2018')
    xqm = request.args.get('xqm','12')
    client = Core(usename, password)
    # client = Core("17061211", "aixiao74525.")
    client.login()
    data = client.getTable(xnm,xqm)
    return jsonify(data)

@app.route('/score/', methods=['GET','POST'])

def score():
    if request.method == 'GET':
        usename = request.args['username']
        password = request.args['password']
    else:
        usename = request.form['username']
        password = request.form['password']
    xnm = request.args.get('xnm','2018')
    xqm = request.args.get('xqm','12')
    client = Core(usename, password)
    # client = Core("17061211", "aixiao74525.")
    client.login()
    data = client.getScore(xnm,xqm)
    return jsonify(data)

@app.route('/login/', methods=['GET','POST'])

def login():
    if request.method == 'POST':
    	usename = request.form['username']
    	password = request.form['password']
    else:
    	usename = request.args['username']
    	password = request.args['password']
    client = Core(usename, password)
    # client = Core("17061211", "aixiao74525.")
    client.login()
    return jsonify({'status':1,'msg':'success'})

@app.errorhandler(400) 
def error(e): 
    print(e)
    return jsonify({'status':0,'msg':str(e)})

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'status':0,'msg':str(e)})
if __name__ == '__main__':
    # 课程安排 POST 查询入口
    app.run(host="0.0.0.0", port=8383)
    # classTableUrl = "http://218.61.108.169/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151"
    # # xnm 所选学年  2017 就是 2017-2018, 2016 就是2016-2017
    # # xqm 所需学期  3 是第一学期，12 是第二学期
    # data = [
    #     ("xnm", "2018"),
    #     ("xqm", "12")
    # ]
    # client = Core("17061211", "aixiao74525.").login()
    # response = client.post(classTableUrl,
    #                        data=data
    #                        )
    # dic = response.json()
    # print(dic)
    # # b = TablesOP().setFormatDict(dic)
    # # a = commandShowTables(b)
    # # a.showTables()
