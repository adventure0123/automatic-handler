#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
自动发微博
'''
import cookielib
import linecache
import re
import time
import os
import  random
import filterStr
import requests
from numpy.numarray import session

agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
headers = {
    'User-Agent': agent
}

session = requests.session()
#session.cookies = cookielib.LWPCookieJar('usercookies/shanjinglp430@163.com.txt')

def getuid():
    try:
        session.cookies.load(ignore_discard=True, ignore_expires=True)
    except:
        print(u"没有检测到cookie文件")
        return False
    url = "http://weibo.com/"
    my_page = session.get(url, headers=headers)
    content=my_page.content
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


def unfollow(folleruid):
    data = {
        "uid": folleruid,
        # "refer_flag": 1005050001
    }
    url="http://weibo.com/aj/f/unfollow?ajwvr=6"
    headers["Referer"] = "http://weibo.com"
    result = session.post(url, data=data, headers=headers)
    print result

def retweet(message,mid):
    data={
        "reason":message,
        "mid": mid
    }
    url="http://weibo.com/aj/v6/mblog/forward?ajwvr=6&__rnd="+ str(time.time() * 1000)
    headers["Referer"] = "http://weibo.com"
    result = session.post(url, data=data, headers=headers)
    print result.content
    print result


def agree(mid):
    data={
        "mid":mid
    }
    url="http://weibo.com/aj/v6/like/add?ajwvr=6"
    headers["Referer"] = "http://weibo.com"
    result = session.post(url, data=data, headers=headers)
    print result

def disagree(mid):
    data = {
        "mid": mid,
        "qid": "heart"
    }
    url = "http://weibo.com/aj/v6/like/add?ajwvr=6"
    headers["Referer"] = "http://weibo.com"
    result = session.post(url, data=data, headers=headers)
    print result

def getcookies(filePath):
    filePath=os.curdir+'/'+filePath
    pathDir = os.listdir(filePath)
    print pathDir
    for allDir in pathDir:
        child = os.path.join('%s%s' % (filePath, allDir))
        print child.decode('gbk')  # .decode('gbk')是解决中文显示乱码问题
    '''users = {}
    f = open(filePath, "r")
    lines = []
    try:
        lines = f.readlines()  # 读取全部内容
    except Exception, e:
        print e
    finally:
        f.close()
    for line in lines:
        s = line.strip("\n").split("----")
        if (len(s) == 2):
            users[s[0]] = s[1]
    return users'''

def reandomMessage(path):
    path=os.curdir+'/'+path
    f = open(path, "r")
    count = len(f.readlines())  # 获取行数
    hellonum = random.randrange(1, count, 1)  # 生成随机行数
    return linecache.getline(path, hellonum).decode('gbk')  # 随机读取某行
    #a =   # 1-9中生成随机数

if __name__ == '__main__':
    #uid=getuid()
    #print uid
    #postMessage("hello",uid)
    #follow(1445962081,uid)
    #unfollow(1445962081)
    #retweet("retweet",4029147573933414)
    #agree(4029147573933414)

    ##群发微博
    filePath='/usercookies'
    filePath = os.curdir + '/' + filePath
    pathDir = os.listdir(filePath)
    #uids = [5770461802, 5886297972, 5884936920, 5886303996, 5886297997, 5884921231]
    print pathDir
    for allDir in pathDir:
        cookiePath=filePath+"/"+allDir
        session.cookies = cookielib.LWPCookieJar(cookiePath)
        try:
            uid=getuid()
            print uid
        except Exception,e:
            print "uid error---->"+allDir
            print e

        #print allDir
        #print uid
        # print '------------'
        # for id in uids:
        #     if str(id)!=str(uid):
        #         follow(id)
        #follow(2567198343)
        #msg="永远支持你:)"
        #retweet("宇宙真是太漂亮了！！！！[哆啦A梦吃惊]",4054406444259255)
        try:
            msg=reandomMessage('weiboText/weibo.txt')
            while filterStr.filterStr(msg):
                msg=reandomMessage('weiboText/weibo.txt')
            postMessage(msg,uid)
            #retweet("奥黑都要下台了，还在这BB。[doge]",4054095960005856)##转发微博
        except Exception,e:
            print "error-------->"+allDir+"------->"+uid
            print e

