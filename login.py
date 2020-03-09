#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/9/16 22:19
# @Author  : Dawnnnnnn
# @Contact: 1050596704@qq.com
import base64
import random
import requests
import rsa
import string
from urllib import parse
import hashlib

# temporary app parameter
appkey = '4409e2ce8ffd12b8'
build = '101800'
# device = 'android_tv_yst'
mobi_app = 'android_tv_yst'
app_secret = '59b43e04ad6965f34319062b478f83dd'


class BiliLogin:
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"

    def __init__(self):
        self.cookie = ""
        self.access_token = ""

    def post(self, url, data=None, headers=None, json=None, decode=True,
             timeout=10):
        try:
            response = requests.post(url, data=data, headers=headers,
                                     json=json,
                                     timeout=timeout)
            return response.json() if decode else response.content
        except:
            return None

    def get(self, url, headers=None, decode=True, timeout=10):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            return response.json() if decode else response.content
        except:
            return None

    def getSign(self, param):
        salt = "59b43e04ad6965f34319062b478f83dd"
        signHash = hashlib.md5()
        signHash.update(f"{param}{salt}".encode())
        return signHash.hexdigest()

    def access_token_2_cookies(self, access_token):
        params = f"access_key={access_token}&appkey={appkey}&gourl=https%3A%2F%2Faccount.bilibili.com%2Faccount%2Fhome"
        url = f"https://passport.bilibili.com/api/login/sso?{params}&sign={self.getSign(params)}"
        response = requests.get(url, allow_redirects=False)
        return response.cookies.get_dict(domain=".bilibili.com")

    # 登录
    def login(self, username, password):
        self.username, self.password = username, password
        appKey = "4409e2ce8ffd12b8"
        url = "https://passport.snm0516.aisee.tv/api/oauth2/getKey"
        data = {'appkey': appKey,
                'sign': self.getSign(f"appkey={appKey}")}
        response = self.post(url, data=data)
        if response and response.get('code') == 0:
            keyHash = response['data']['hash']
            pubKey = rsa.PublicKey.load_pkcs1_openssl_pem(
                response['data']['key'].encode())
        else:
            print(f"Key获取失败 {response}")
            return False
        url = "https://passport.snm0516.aisee.tv/api/tv/login"
        param = f"appkey={appkey}&build={build}&captcha=&channel=master&guid=XYEBAA3E54D502E37BD606F0589A356902FCF&mobi_app={mobi_app}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{keyHash}{self.password}'.encode(), pubKey)))}&platform=android&token=5598158bcd8511e2&ts=0&username={parse.quote_plus(self.username)}"
        data = f"{param}&sign={self.getSign(param)}"
        headers = {'Content-type': "application/x-www-form-urlencoded"}
        response = self.post(url, data=data, headers=headers)
        while response and response.get('code') == -105:
            self.cookie = f"sid={''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
            url = "https://passport.snm0516.aisee.tv/api/captcha?token=5598158bcd8511e2"
            headers = {'Cookie': self.cookie,
                       'Host': "snm0516.aisee.tv",
                       'User-Agent': BiliLogin.ua}
            response = self.get(url, headers=headers, decode=False)
            if response is None:
                continue
            url = "http://106.75.36.27:19951/captcha/v1"
            img = base64.b64encode(response)
            img = str(img, encoding="utf-8")
            json = {'image': img}
            response = self.post(url, json=json, decode=True)
            print(f"验证码识别结果为: {response['message']}")
            url = "https://passport.snm0516.aisee.tv/api/tv/login"
            param = f"appkey={appKey}&captcha={response['message']}&channel=master&guid=XYEBAA3E54D502E37BD606F0589A356902FCF&mobi_app={mobi_app}&password={parse.quote_plus(base64.b64encode(rsa.encrypt(f'{keyHash}{self.password}'.encode(), pubKey)))}&platform=android&token=5598158bcd8511e2&ts=0&username={parse.quote_plus(self.username)}"
            data = f"{param}&sign={self.getSign(param)}"
            headers = {'Content-type': "application/x-www-form-urlencoded",
                       'Cookie': self.cookie}
            response = self.post(url, data=data, headers=headers)
        if response and response.get('code') == 0:
            cookie_info = self.access_token_2_cookies(response['data']['token_info']['access_token'])
            for key, value in cookie_info.items():
                self.cookie = self.cookie + key + "=" + value + ";"

            self.access_token = response['data']['token_info']['access_token']
            print(f"{self.username}登录成功 {self.cookie} {self.access_token}")
            with open("cookies.txt", "a+", encoding="utf-8")as f:
                f.write(f"{self.username}----{self.cookie}----{self.access_token}\n")
            return self.username, self.cookie, self.access_token
        else:
            print(f"{self.username}登录失败 {response}")
