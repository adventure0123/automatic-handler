#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- requests (必须)
- rsa (必须)
- pillow (可选)
Info
- author : "xchaoinfo"
- email  : "xchaoinfo@qq.com"
- date   : "2016.3.7"
'''
import cookielib
import json
import time
import base64
import rsa
import binascii
import requests
import re
import random
try:
    from PIL import Image
except:
    pass
try:
    from urllib.parse import quote_plus
except:
    from urllib import quote_plus
import cookies_new
import weibo_postMessage
import filterStr
'''
如果没有开启登录保护，不用输入验证码就可以登录
如果开启登录保护，需要输入验证码

'''

# import os
# os.environ["http_proxy"] = "http://101.91.21.91:8123"

# 构造 Request headers
agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
headers = {
    'User-Agent': agent
}

session = requests.session()
# session.cookies = cookielib.LWPCookieJar('cookies.txt')
# proxies= {'http' : 'http://183.194.15.22:8118'}
# session.proxies = proxies
# 访问 初始页面带上 cookie
index_url = "http://weibo.com/login.php"
try:
    session.get(index_url, headers=headers, timeout=2)
except:
    session.get(index_url, headers=headers)
try:
    input = raw_input
except:
    pass


def get_su(username):
    """
    对 email 地址和手机号码 先 javascript 中 encodeURIComponent
    对应 Python 3 中的是 urllib.parse.quote_plus
    然后在 base64 加密后decode
    """
    username_quote = quote_plus(username)
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))
    return username_base64.decode("utf-8")


# 预登陆获得 servertime, nonce, pubkey, rsakv
def get_server_data(su):
    pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
    pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
    pre_url = pre_url + str(int(time.time() * 1000))
    pre_data_res = session.get(pre_url, headers=headers)

    sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))

    return sever_data


# print(sever_data)


def get_password(password, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
    message = message.encode("utf-8")
    passwd = rsa.encrypt(message, key)  # 加密
    passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
    return passwd


def get_cha(pcid):
    cha_url = "http://login.sina.com.cn/cgi/pin.php?r="
    cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
    cha_url = cha_url + pcid
    cha_page = session.get(cha_url, headers=headers)
    with open("cha.jpg", 'wb') as f:
        f.write(cha_page.content)
        f.close()
    try:
        im = Image.open("cha.jpg")
        im.show()
        im.close()
    except:
        print(u"请到当前目录下，找到验证码后输入")


def login(username, password):
    # su 是加密后的用户名
    su = get_su(username)
    sever_data = get_server_data(su)
    servertime = sever_data["servertime"]
    nonce = sever_data['nonce']
    rsakv = sever_data["rsakv"]
    pubkey = sever_data["pubkey"]
    showpin = sever_data["showpin"]
    password_secret = get_password(password, servertime, nonce, pubkey)

    postdata = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'useticket': '1',
        'pagerefer': "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
        'vsnf': '1',
        'su': su,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv': rsakv,
        'sp': password_secret,
        'sr': '1366*768',
        'encoding': 'UTF-8',
        'prelt': '115',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
        }
    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
    if showpin == 0:
        login_page = session.post(login_url, data=postdata, headers=headers)
    else:
        pcid = sever_data["pcid"]
        get_cha(pcid)
        postdata['door'] = input(u"请输入验证码")
        print postdata
        login_page = session.post(login_url, data=postdata, headers=headers)
    login_loop = (login_page.content.decode("GBK"))
    pa = r'location\.replace\([\'"](.*?)[\'"]\)'
    loop_url = re.findall(pa, login_loop)[0]
    print(loop_url.decode("gbk"))
    # 此出还可以加上一个是否登录成功的判断，下次改进的时候写上
    login_index = session.get(loop_url, headers=headers)
    #print login_index.content.decode("gbk")
    uuid = login_index.text
    uuid_pa = r'"uniqueid":"(.*?)"'
    uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
    web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
    weibo_page = session.get(web_weibo_url, headers=headers)
    #print weibo_page.content
    weibo_pa = r'<title>(.*?)</title>'
    # print(weibo_page.content.decode("utf-8"))
    userID = re.findall(weibo_pa, weibo_page.content.decode("utf-8", 'ignore'), re.S)[0]
    #print session.cookies
    #session.cookies.save(ignore_discard=True, ignore_expires=True)
    print(u"欢迎你 %s, 你在正在使用 xchaoinfo 写的模拟登录微博" % userID)

def postMessage(message,uid):
    print message
    data = {
        "text": message,
    }
    url = "http://weibo.com/aj/mblog/add?ajwvr=6&__rnd=" + str(time.time() * 1000)
    headers["Referer"] = "http://weibo.com/"+str(uid)+"/profile"
    result=session.post(url,data=data,headers=headers)
    #print result.content
    if(result.status_code==200):
        print "post success"
    else:
        print "post fail"

def mlogin(username, password):
    print username
    username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    data = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    login_url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
    #session = requests.session()
    res = session.post(login_url, data=data)
    if(res.status_code!=200):
        print "--------->log err"
        return None
    jsonStr = res.content.decode('gbk')
    info = json.loads(jsonStr)
    session.cookies.save(ignore_discard=True, ignore_expires=True)
    print info


    if info["retcode"] != "0":
        #info = json.loads(info)
        #print username
        print info["reason"]
    return info["uid"]

def getuid():
    # try:
    #     session.cookies.load(ignore_discard=True, ignore_expires=True)
    # except:
    #     print(u"没有检测到cookie文件")
    #     return False
    url = "http://weibo.com/"
    my_page = session.get(url, headers=headers)
    content=my_page.content
    print content
    r = re.compile(r"\$CONFIG\['uid'\]='(.*?)';")#get uid
    uid = r.findall(content)[0]
    return uid


def postMessage(message,uid):
    print message
    data = {
        "text": message,
    }
    url = "http://weibo.com/aj/mblog/add?ajwvr=6&__rnd=" + str(time.time() * 1000)
    headers["Referer"] = "http://weibo.com/"+str(uid)+"/profile"
    result=session.post(url,data=data,headers=headers)
    #print result.content
    if(result.status_code==200):
        print "post success"
    else:
        print "post fail"

def follow(folleruid):
    data={
        "uid":folleruid,
        "refer_flag":1005050001
    }
    url = "http://weibo.com/aj/f/followed?ajwvr=6&__rnd=" + str(time.time() * 1000)
    headers["Referer"] = "http://weibo.com"
    result = session.post(url, data=data, headers=headers)
    print result
    if (result.status_code == 200):
        print "follow success"
    else:
        print "follow fail"


def retweet(message, mid):
    data = {
        "reason": message,
        "mid": mid
    }
    url = "http://weibo.com/aj/v6/mblog/forward?ajwvr=6&__rnd=" + str(time.time() * 1000)
    headers["Referer"] = "http://weibo.com"
    result = session.post(url, data=data, headers=headers)
    print result.content
    print result


if __name__ == "__main__":
    f = open("users.txt", "r")
    lines = []
    try:
        lines = f.readlines()  # 读取全部内容
    except Exception, e:
        print e
    finally:
        f.close()

    message = open("weiboText/weibo.txt", "r")
    content = []
    try:
        content = message.readlines()  # 读取全部内容
    except Exception, e:
        print e
    finally:
        message.close()
    # print  random.choice(content).decode('gbk')
    # proxy = proxyHandler.getProxy()
    # print proxy
    # proxy="125.121.120.71:808"
    proxy = None
    times = 0
    usetime = 0
    index = 0
    proxies = None
    while index < len(lines):
        users = lines[index]
        s = users.strip("\n").split("----")
        user = s[0]
        password = s[1]
        # print s
        print user
        print password
        if proxy == None or usetime > 2:
            proxyUrl = "http://tpv.daxiangdaili.com/ip/?tid=558661331252937&num=1&category=2&sortby=time&filter=on"
            proxy = requests.get(url=proxyUrl).content
            print proxy
            proxies = {
                "http": "http://" + proxy
            }
            times = times + 1
            print proxies
            session.proxies = proxies
        try:
            res = session.get("http://www.icanhazip.com/", timeout=3)
            print res.content
            login(user, password)
            uid = getuid()
            print uid

            msg = random.choice(content)
            while filterStr.filterStr(msg):
                msg = random.choice(content)
            # print msg
            print msg.decode('gbk')
            postMessage(msg, uid)

            follow('2113264853')
            retweet('转发微博','4056230731077908')
            #retweet('@麦田守望者0123 抽奖了！', '4056523229467680')
            follow('5400531923')
            follow('6076836387')

            index = index + 1
            usetime = usetime + 1
        except Exception, e:
            print e
            proxy = None
            usetime = 0
            # time.sleep(1)#休眠1秒
    print times




'''res = session.get("http://wwww.icanhazip.com/", timeout=2)
    print res.content
    #username = input(u'用户名：')
    #password = input(u'密码：')
    username="lwei2037@163.com"
    password="qa963210"
    login(username, password)
    uid = getuid()
    print uid
    msg = weibo_postMessage.reandomMessage('weiboText/weibo.txt')
    while filterStr.filterStr(msg):
        msg = weibo_postMessage.reandomMessage('weiboText/weibo.txt')
    print msg
    postMessage(msg,uid)'''
    # users = cookies_new.getUser("users.txt")
    # for username in users:
    #     uid=mlogin(username,users[username])
        #print uid
    #print uid
