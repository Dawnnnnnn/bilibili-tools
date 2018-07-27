import random
import asyncio
import requests
import time
import json
import hashlib
import rsa
import base64
import re
import datetime
from urllib import parse


def CurrentTime():
    currenttime = str(int(time.mktime(datetime.datetime.now().timetuple())))
    return currenttime

class login():
    cookies = ""
    username = input("输入用户名:")
    password = input("输入密码:")
    headers = {
        "Host": "api.bilibili.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": cookies
    }
    csrf = ""
    uid = ""
    access_key = ""

    async def calc_sign(self,str):
        str = str + "560c52ccd288fed045859ed18bffd973"
        hash = hashlib.md5()
        hash.update(str.encode('utf-8'))
        sign = hash.hexdigest()
        return sign

    async def get_pwd(self, username, password):
        url = 'https://passport.bilibili.com/api/oauth2/getKey'
        temp_params = 'appkey=1d8b6e7d45233436'
        sign = await self.calc_sign(temp_params)
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

    async def login(self):
        url = "https://passport.bilibili.com/api/v2/oauth2/login"
        user, pwd = await self.get_pwd(login.username, login.password)
        temp_params = 'appkey=1d8b6e7d45233436&password=' + pwd + '&username=' + user
        sign = await self.calc_sign(temp_params)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        payload = temp_params + "&sign=" + sign
        response = requests.post(url, data=payload, headers=headers)
        try:
            cookie = (response.json()['data']['cookie_info']['cookies'])
            cookie_format = ""
            for i in range(0, len(cookie)):
                cookie_format = cookie_format + cookie[i]['name'] + "=" + cookie[i]['value'] + ";"
            s1 = re.findall(r'bili_jct=(\S+)', cookie_format, re.M)
            s2 = re.findall(r'DedeUserID=(\S+)', cookie_format, re.M)
            login.cookies = cookie_format
            login.headers = {
                "Host": "api.bilibili.com",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cookie": login.cookies
            }
            login.csrf = (s1[0]).split(";")[0]
            login.uid = (s2[0].split(";")[0])
            login.access_key = response.json()['data']['token_info']['access_token']
        except:
            print("登录失败，回显为:", response.json())


class judge(login):

    def randomint(self):
        return ''.join(str(random.choice(range(10))) for _ in range(17))

    def CurrentTime(self):
        millis = int((time.time() * 1000))
        return str(millis)

    async def caseObtain(self):
        try:
            url = 'http://api.bilibili.com/x/credit/jury/caseObtain'
            data = {'jsonp':'jsonp','csrf':login.csrf}
            response = requests.post(url, headers=login.headers,data=data)
            temp = response.json()
            print(temp)
            if temp['code'] == 0:
                id = temp['data']['id']
                return id
            if temp['code'] == -101:
                print("cookie失效,尝试重新登录!")
                await self.login()
                await self.judge()
            if temp['code'] == 25014 or 25008:
                print("今日的案件已经审理完毕了噢~,休眠六小时后会再次开始审理")
                await asyncio.sleep(21600)
                await self.judge()
        except:
            print("caseObtain模块出错")
            await self.judge()

    async def check(self):
        vote = 4
        id = await self.caseObtain()
        headers = {
            "Host": "api.bilibili.com",
            "Referer": "https://www.bilibili.com/judgement/vote/" + str(id),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": login.cookies
        }
        try:
            url = "https://api.bilibili.com/x/credit/jury/juryCase?jsonp=jsonp&callback=jQuery1720" + str(
                self.randomint()) + "_" + self.CurrentTime() + "&cid=" + str(id) + "&_=" + self.CurrentTime()
            response = requests.get(url, headers=headers)
            print(response.text)
            temp = (response.text[42:-1])
            temp = json.loads(temp)
            print(temp)
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
            await asyncio.sleep(120)
            await self.judge()

    async def judge(self):
        try:
            id, vote = await self.check()
            url = 'http://api.bilibili.com/x/credit/jury/vote'
            payload = {
                "jsonp": "jsonp",
                "cid": id,
                "vote": vote,
                "content": "",
                "likes": "",
                "hates": "",
                "attr": "1",
                "csrf": login.csrf
            }
            response = requests.post(url, headers=login.headers, data=payload)
            print(response.json())
        except:
            print('judge出错')

    async def query_reward(self):
        url = "https://account.bilibili.com/home/reward"
        headers = {
            "Referer": "https://account.bilibili.com/account/home",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "Cookie":login.cookies
        }
        response = requests.get(url,headers=headers)
        iflogin = response.json()['data']['login']
        ifwatch_av = response.json()['data']['watch_av']
        ifshare_av = response.json()['data']['share_av']
        ifgive_coin = response.json()['data']['coins_av']
        return [iflogin,ifwatch_av,ifshare_av,int(ifgive_coin)]

    async def get_attention(self):
        top50_attention_list = []
        url = "https://api.bilibili.com/x/relation/followings?vmid=" + str(login.uid) + "&ps=50&order=desc"
        headers = {
            "Host": "api.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": login.cookies
        }
        response = requests.get(url, headers=headers)
        checklen = len(response.json()['data']['list'])
        for i in range(0, checklen):
            uids = (response.json()['data']['list'][i]['mid'])
            top50_attention_list.append(uids)
        return top50_attention_list

    async def getsubmit_video(self):
        top50_attention_list = await self.get_attention()
        video_list = []
        for mid in top50_attention_list:
            url = "https://space.bilibili.com/ajax/member/getSubmitVideos?mid=" + str(mid) + "&pagesize=100&tid=0"
            response = requests.get(url)
            datalen = len(response.json()['data']['vlist'])
            for i in range(0, datalen):
                aid = response.json()['data']['vlist'][i]['aid']
                video_list.append(aid)
        return video_list

    async def givecoin(self):
        video_list = await self.getsubmit_video()
        url = "https://api.bilibili.com/x/web-interface/coin/add"
        aid = video_list[random.randint(0, len(video_list))]
        data = {
            "aid": aid,
            "multiply": "1",
            "cross_domain": "true",
            "csrf": login.csrf
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "Referer": "https://www.bilibili.com/video/av" + str(aid),
            "Origin": "https://www.bilibili.com",
            "Host": "api.bilibili.com",
            "Cookie": login.cookies
        }
        response = requests.post(url, data=data, headers=headers)
        print("coin_task:",response.text)

        if response.json()['code'] != 0:
            await self.givecoin()
        await asyncio.sleep(10)

    async def get_cid(self,aid):
        url = "https://www.bilibili.com/widget/getPageList?aid="+str(aid)
        response = requests.get(url)
        cid = response.json()[0]['cid']
        return cid

    async def share(self):
        video_list = await self.getsubmit_video()
        aid = video_list[random.randint(0, len(video_list))]
        url1 = "https://app.bilibili.com/x/v2/view/share/add"
        headers = {
            "User-Agent": "Mozilla/5.0 BiliDroid/5.26.3 (bbcallen@gmail.com)",
            "Host": "app.bilibili.com",
            "Cookie": "sid=8wfvu7i7"
        }
        ts = CurrentTime()
        temp_params = "access_key="+login.access_key+"&aid="+str(aid)+"&appkey=1d8b6e7d45233436&build=5260003&from=7&mobi_app=android&platform=android&ts="+str(ts)
        sign = await self.calc_sign(temp_params)
        data = {
            "access_key":login.access_key,
            "aid":aid,
            "appkey":"1d8b6e7d45233436",
            "build":"5260003",
            "from":"7",
            "mobi_app":"android",
            "platform":"android",
            "ts":ts,
            "sign":sign
        }
        response = requests.post(url1,headers=headers,data=data)
        print("分享视频:",response.json())


    async def watch_av(self,aid,cid):
        url = "https://api.bilibili.com/x/report/web/heartbeat"
        headers = {
            "Host": "api.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "Referer": "https://www.bilibili.com/video/av"+str(aid),
            "Cookie":login.cookies
        }
        data = {
            "aid":aid,
            "cid":cid,
            "mid":login.uid,
            "csrf":login.csrf,
            "played_time":"0",
            "realtime":"0",
            "start_ts":self.CurrentTime(),
            "type":"3",
            "dt":"2",
            "play_type":"1"
        }

        response = requests.post(url,headers=headers,data=data)

        print("watch_Av_state:",response.text)

    async def judge_run(self):
        while 1:
            try:
                await self.judge()
                await asyncio.sleep(random.randint(12,43))
            except:
                print('judge_run出错')

    async def coin_run(self):
        while 1:
            try:
                i = await self.query_reward()
                coin_exp = i[3]
                while coin_exp < 50:
                    await self.givecoin()
                    coin_exp = coin_exp + 10
                if coin_exp == 50:
                    print("投币任务完成")
                    await asyncio.sleep(86400)
                    await self.coin_run()
            except:
                print("coin_run出错")

    async def share_run(self):
        while 1:
            try:
                await self.share()
                print("分享任务完成")
                await asyncio.sleep(21600)
            except:
                print("share_run出错")

    async def watch_run(self):
        while 1:
            try:
                video_list = await self.getsubmit_video()
                aid = video_list[random.randint(0, len(video_list))]
                cid = await self.get_cid(aid)
                await self.watch_av(aid,cid)
                await asyncio.sleep(21600)
            except:
                print("watch_run出错")



loop = asyncio.get_event_loop()
tasks1 = [
    judge().login()
]
loop.run_until_complete(asyncio.wait(tasks1))

loop2 = asyncio.get_event_loop()

tasks2 = [
    judge().coin_run(),
    judge().share_run(),
    judge().watch_run(),
    judge().judge_run()

]
loop.run_until_complete(asyncio.wait(tasks2))