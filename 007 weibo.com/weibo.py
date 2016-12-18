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

'''
如果没有开启登录保护，不用输入验证码就可以登录
如果开启登录保护，需要输入验证码

'''


# 构造 Request headers
agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
headers = {
    'User-Agent': agent
}

session = requests.session()
session.cookies = cookielib.LWPCookieJar('cookies.txt')

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
    print username+"   "+password
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
        login_page = session.post(login_url, data=postdata, headers=headers)
    login_loop = (login_page.content.decode("GBK"))
    # print(login_loop)
    pa = r'location\.replace\([\'"](.*?)[\'"]\)'
    loop_url = re.findall(pa, login_loop)[0]
    # print(loop_url)
    # 此出还可以加上一个是否登录成功的判断，下次改进的时候写上
    login_index = session.get(loop_url, headers=headers)
    uuid = login_index.text
    uuid_pa = r'"uniqueid":"(.*?)"'
    uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
    web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
    weibo_page = session.get(web_weibo_url, headers=headers)
    weibo_pa = r'<title>(.*?)</title>'
    # print(weibo_page.content.decode("utf-8"))
    userID = re.findall(weibo_pa, weibo_page.content.decode("utf-8", 'ignore'), re.S)[0]
    #print session.cookies
    session.cookies.save(ignore_discard=True, ignore_expires=True)
    print(u"欢迎你 %s, 你在正在使用 xchaoinfo 写的模拟登录微博" % userID)


def mlogin(username, password):
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
    return info["uid"]
    # if info["retcode"] == "0":
    #     cookies = session.cookies.get_dict()
    #     cookies = [key + "=" + value for key, value in cookies.items()]
    #     cookies = "; ".join(cookies)
    #     session.headers["cookie"] = cookies
    #     print cookies
    #     #session.cookies=cookies
    # else:
    #     raise Exception("login fail:%s" % info["reason"])
    # print session
    #session.cookies = cookielib.LWPCookieJar('cookies.txt')

    #return  session

if __name__ == "__main__":
    #username = input(u'用户名：')
    #password = input(u'密码：')
    #username="18445965029"
    #password="wang23456"
    #login(username, password)
    users = cookies_new.getUser("users.txt")
    for username in users:
        uid=mlogin(username,users[username])
        print uid
    #print uid
