# -*- coding:utf-8 -*-
import random
import urllib
import urllib2
from bs4 import BeautifulSoup
import requests
import weiboH5
import weibo_postMessage
import filterStr
import cookies_new

requests.adapters.DEFAULT_RETRIES = 5
#users = cookies_new.getUser("users.txt")

def getProxy(page):
    User_Agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
    header = {}
    header['User-Agent'] = User_Agent

    url = 'http://www.xicidaili.com/wn/'+str(page)
    req = urllib2.Request(url, headers=header)
    res = urllib2.urlopen(req).read()

    soup = BeautifulSoup(res, "html.parser")
    ips = soup.findAll('tr')
    result = []
    for x in range(1, len(ips)):
        ip = ips[x]
        # print ip
        tds = ip.findAll("td")
        # print tds[4].contents[0]
        # if tds[4].contents[0] == u"透明":
        #     continue
        proxy = tds[1].contents[0] + ":" + tds[2].contents[0]
        #print proxy
        url = "https://icanhazip.com/"
        # proxy_handler = urllib2.ProxyHandler({'http': proxy})
        # opener = urllib2.build_opener(proxy_handler)
        # res = opener.open(url).read()
        proxy_host = "http://" + proxy
        proxy_temp = {"https": proxy_host}
        try:
            res = requests.get(url, proxies=proxy_temp, timeout=2)
            #print res.content
            if res.status_code == 200:
                print proxy
                print "success"
                weibo = weiboH5.Weibo("17130971274", 'ak123654', proxy_temp)
                uid = weibo.login("17130971274", "ak123654")
                print uid
                msg = weibo_postMessage.reandomMessage('weiboText/weibo.txt')
                while filterStr.filterStr(msg):
                    msg = weibo_postMessage.reandomMessage('weiboText/weibo.txt')
                print msg
                weibo.post_new(msg)
                return

                result.append(proxy)
                # return result
                # print res
                # result.append(proxy)
        except Exception, e:
            print e
            continue
            # print ips
    return result
    # f = open("proxy", "a")
    # try:
    #     for x in range(1, len(ips)):
    #         ip = ips[x]
    #         tds = ip.findAll("td")
    #         ip_temp = tds[2].contents[0] + "\t" + tds[3].contents[0] + "\n"
    #         # print tds[2].contents[0]+"\t"+tds[3].contents[0]
    #         f.write(ip_temp)
    # except Exception, e:
    #     print e
    # finally:
    #     f.close()


if __name__ == "__main__":
    # imgPath='simple.jpeg'
    for index in range(1,100):
        proxies = getProxy(index)
    # print proxies
    # print random.choice(proxies)
