import random
import requests
import time
import json
import hashlib
import rsa
import base64
import re
from urllib import parse

class login():
    def __init__(self):
        self.cookies = ""
        self.username = input("账号:")
        self.password = input("密码:")
        self.headers = {
            "Host": "api.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": self.cookies
        }
        self.csrf = ""

    def calc_sign(self, str):
        str = str + "560c52ccd288fed045859ed18bffd973"
        hash = hashlib.md5()
        hash.update(str.encode('utf-8'))
        sign = hash.hexdigest()
        return sign

    def get_pwd(self, username, password):
        url = 'https://passport.bilibili.com/api/oauth2/getKey'
        temp_params = 'appkey=1d8b6e7d45233436'
        sign = self.calc_sign(temp_params)
        params = {'appkey': '1d8b6e7d45233436', 'sign': sign}
        response = requests.post(url, data=params)
        value = response.json()['data']
        key = value['key']
        Hash = str(value['hash'])
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(key.encode())
        password = base64.b64encode(rsa.encrypt((Hash + password).encode('utf-8'), pubkey))
        password = parse.quote_plus(password)
        username = parse.quote_plus(username)
        return username, password

    def login(self):
        url = "https://passport.bilibili.com/api/v2/oauth2/login"
        user, pwd = self.get_pwd(self.username, self.password)
        temp_params = 'appkey=1d8b6e7d45233436&password=' + pwd + '&username=' + user
        sign = self.calc_sign(temp_params)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        payload = temp_params + "&sign=" + sign
        response = requests.post(url, data=payload, headers=headers)
        cookie = (response.json()['data']['cookie_info']['cookies'])
        cookie_format = ""
        for i in range(0, len(cookie)):
            cookie_format = cookie_format + cookie[i]['name'] + "=" + cookie[i]['value'] + ";"
        s1 = re.findall(r'bili_jct=(\S+)', cookie_format, re.M)
        self.cookies = cookie_format
        self.headers = {
            "Host": "api.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": self.cookies
        }
        self.csrf = (s1[0]).split(";")[0]

class judge(login):

    def randomint(self):
        return ''.join(str(random.choice(range(10))) for _ in range(17))

    def CurrentTime(self):
        millis = int((time.time() * 1000))
        return str(millis)

    def caseObtain(self):
        try:
            url = 'http://api.bilibili.com/x/credit/jury/caseObtain'
            response = requests.post(url, headers=self.headers)
            temp = response.json()
            print(temp)
            if temp['code'] == 0:
                id = temp['data']['id']
                return id
            if temp['code'] == -101:
                print("cookie失效,尝试重新登录!")
                self.login()
                self.judge()
            if temp['code'] == 25014:
                print("今日的案件已经审理完毕了噢~,休眠六小时后会再次开始审理")
                time.sleep(21600)
                self.judge()
        except:
            print("caseObtain模块出错")

    def check(self):
        vote = 4
        id = self.caseObtain()
        headers = {
            "Host": "api.bilibili.com",
            "Referer": "https://www.bilibili.com/judgement/vote/" + str(id),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": self.cookies
        }
        try:
            url = "https://api.bilibili.com/x/credit/jury/juryCase?jsonp=jsonp&callback=jQuery1720" + str(
                self.randomint()) + "_" + self.CurrentTime() + "&cid=" + str(id) + "&_=" + self.CurrentTime()
            response = requests.get(url, headers=headers)
            temp = (response.text[42:-1])
            temp = json.loads(temp)
            votebreak = temp['data']['voteBreak']
            voteDelete = temp['data']['voteDelete']
            voteRule = temp['data']['voteRule']
            if votebreak > voteDelete:
                vote = 1
            if votebreak < voteDelete:
                vote = 4
            if (voteRule > votebreak) and (voteRule > voteDelete):
                vote = 2
            return id, vote
        except:
            print("check模块出错")

    def judge(self):
        id, vote = self.check()
        url = 'http://api.bilibili.com/x/credit/jury/vote'
        payload = {
            "jsonp": "jsonp",
            "cid": id,
            "vote": vote,
            "content": "",
            "likes": "",
            "hates": "",
            "attr": "1",
            "csrf": self.csrf
        }
        response = requests.post(url, headers=self.headers, data=payload)
        print(response.json())

    def run(self):
        self.login()
        while 1:
            self.judge()
            time.sleep(random.randint(12,43))

judge().run()
