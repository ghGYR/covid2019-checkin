import urllib.request as rq
from urllib import parse
from http import cookiejar
import json
import time
import gzip
header={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer":"https://m.ruc.edu.cn/uc/wap/login",
        "Origin":"https://m.ruc.edu.cn",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "X-Requested-With": "XMLHttpRequest"
    }
def submit(cookie,data,geo_api_info,province,city):
    url="https://m.ruc.edu.cn/ncov/wap/default/save"
    header["Cookie"]=cookie
    data['geo_api_info']=geo_api_info
    data['province']=province
    data['area']=province+" "+city
    data=bytes(parse.urlencode(data),encoding="utf8")
    req = rq.Request(url=url, data=data, headers=header, method='POST')
    try:
        req = rq.urlopen(req)
        req=req.read().decode('utf-8')
        msg=json.loads(req)['m']
    except:
        msg="submit failed"
    return msg

def info_push(corpid,Secret,user,msg):
    url1 = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}'
    req=rq.urlopen(url1.format(corpid,Secret))
    access_token = json.loads(req.read().decode('utf-8'))['access_token']
    print(msg)
    data = { 
        "touser" : user,
        "msgtype": "text",
        "agentid" : 1000002,                       
        "text" : {
            "content" : "校园疫情防控自动打卡提醒:\n"+msg+"\n"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        },
        "safe":0
    }
    data=json.dumps(data)
    data=bytes(data,encoding="utf8")
    url2="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}"
    req = rq.Request(url=url2.format(access_token), data=data, method='POST')
    req = rq.urlopen(req)
    print(req.read().decode('utf-8'))

def login(username,password):
    url="https://m.ruc.edu.cn/uc/wap/login/check"
    data={
    "username": username,
    "password": password
    }
    data=bytes(parse.urlencode(data),encoding="utf8")
    cookie=cookiejar.CookieJar()
    handler=rq.HTTPCookieProcessor(cookie)
    opener=rq.build_opener(handler)
    req = rq.Request(url=url, data=data,headers=header, method='POST')
    rep=opener.open(req)
    rep= rep.read().decode('utf-8')
    #print(rep)
    cookie_s=""
    msg=json.loads(rep)
    print(msg)
    if msg['e']==0:
        for item in cookie:
            cookie_s+=item.name+"="+item.value+';'
    print(cookie_s)
    return cookie_s

def checkin(config):
    cookie=config['cookie']
    if cookie=="":
        try:
            cookie=login(config['username'],config['password'])
        except:
            cookie=""
            msg="login failed"
    if cookie!="":   
        province=config['location']["addressComponent"]["province"]
        city=config['location']["addressComponent"]["city"]
        geo_api_info=str(config['location'])
        data=config['form'] 
        msg=submit(cookie,data,geo_api_info,province,city)
        if msg=="submit failed":
            msg="Cookie error. Relogin..."
            try:
                cookie=login(config['username'],config['password'])
            except:
                msg+="Failed"
            else:
                msg+=submit(cookie,data,geo_api_info,province,city)
    try:
        info_push(config['wechat_api']['corpid'],config['wechat_api']['Secret'],config['wechat_api']['user'],msg)
    except:
        print("failed push")
if __name__=="__main__":
    import sys
    import json
    import base64
    b64string=sys.argv[1]
    jstring=base64.b64decode(b64string)
    config=json.loads(jstring)
    checkin(config)