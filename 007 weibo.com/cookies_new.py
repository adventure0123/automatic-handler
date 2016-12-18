#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cookielib
import  qrcode

import weibo

def getUser(filePath):
    users={}
    f = open(filePath, "r")
    lines=[]
    try:
        lines = f.readlines()  # 读取全部内容
    except Exception,e:
        print e
    finally:
        f.close()
    for line in lines:
        s=line.strip("\n").split("----")
        if(len(s)==2):
            users[s[0]]=s[1]
    return users


def savecookies(users):
    # username = input(u'用户名：')
    # password = input(u'密码：')
    print users
    for username in users:
        weibo.session.cookies = cookielib.LWPCookieJar('usercookies/'+username+'.txt')

        try:
            weibo.login(username, users[username])
        except Exception,e:
            print "login error------>"+username
            print e
        #print weibo.session

def saveCookiesWithqr():
    qrcode.login();

if __name__ == "__main__":
    #users=getUser("users.txt")
    users={"xianyuekeran4926@163.com":"aaa333"}
    savecookies(users)