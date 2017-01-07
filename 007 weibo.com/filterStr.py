#!/usr/bin/env python
# -*- coding: utf-8 -*-
import  sys
import random
reload(sys)
sys.setdefaultencoding('utf-8')
filters=["图","秒拍","@",'分享','视频','图片','秒拍视频']

'''
判断str中是否有符合过滤规则的字符串
'''
def filterStr(str):
    for filter in filters:
        if filter in str:
            return True
    return False

if __name__ == '__main__':
    #string="分享视频"
    #print filterStr(string)
    message = open("weiboText/weibo.txt", "r")
    content = []
    try:
        content = message.readlines()  # 读取全部内容
    except Exception, e:
        print e
    finally:
        message.close()
    msg = random.choice(content)
    while filterStr(msg):
        msg = random.choice(content)
    print msg.decode('gbk')
    # index=0
    # while index < len(content):
    #     #print content[index]
    #     #print len(content[index])
    #     str=content[index]
    #     print type(str)
    #     str=str[0:141]
    #     if len(str)>140:
    #         print str
    #         print index
    #     index=index+1
    #print filters