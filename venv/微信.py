from urllib import request
from urllib import parse
import requests
import urllib
import re
import lxml.html
from lxml import etree
import cssselect as css
import pandas as pd
import os
import json
import time
from random import shuffle

a = requests.get("http://172.16.4.63:8080/intelligent/getRegions").json()
dic = {}
for i in a:
    dic[i["abbr"]] = i['value']
    for j in i['subs']:
        dic[j["abbr"]] = j['value']
        for k in j['subs']:
            dic[k['abbr']] = k['value']
def getcitycode(str):
    citycode = ""
    for i in dic:
        if i in str:
            citycode = dic[i]
            break
    return citycode


def get_uniqueid(unique_str):

    if unique_str is None or unique_str.__len__() == 0:

        return 0

    hash_code = 0

    unique_str = parse.quote_plus(unique_str, encoding="utf-8")

    for i in unique_str:

        hash_code = hash_code * 31 + ord(i)

    uniqueid = ((hash_code + 0x8000000000000000) & 0xFFFFFFFFFFFFFFFF) - 0x8000000000000000

    return uniqueid

def url_open(url):

    res = request.Request(url)
    res.add_header("User-Agent",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134")
    html = request.urlopen(res,timeout = 60).read().decode()
    return html

def geturllist(html,city):
    url = list()
    p = r'dept.{1,2}" ougrcode="([^<]+class)'
    data = re.findall(p,html)
    a = list()
    b = list()
    for i in data:
        a.append(i[0:9])
        b.append(i[17:len(i)-7])
        url.append("http://lz.gszwfw.gov.cn/gszw/qlqd/showtop.do?groupid=" + i[0:9] + "&webid=" + city + "&groupname=" + urllib.parse.quote(i[17:len(i)-7]))
    getcomp = dict(zip(a,b))
    return([url,getcomp])

def getmark(urllist,city,DN):
    mark = list()
    for url in urllist:
        html = url_open(url)
        p = r'onclick="showdown\(\'([^<]+\')'
        a = re.findall(p,html)
        t = int(len(a)/2)
        a = a[0:t]
        p = r'onclick="showtzxmsb\(\'([^<]+\')'    #考虑是否存在投资项目
        tz = re.findall(p,html)
        if len(tz)!= 0:
            a = a + tz
        for i in a:
            url2 = "http://lz.gszwfw.gov.cn/gszw/qlqd/showdown.do?webid=" + city + "&groupid="+url[53:62] +"&type="+i[0:2]
            html2 = url_open(url2)
            page = re.findall(r'pagecount="[0-9]{1,2}',html2)
            page = int(page[0][11:len(page[0])])
            for page in range(1,page+1):
                url2 = "http://lz.gszwfw.gov.cn/gszw/qlqd/showdown.do?webid=" + city + "&groupid=" + url[53:62] + "&type=" + i[0:2] + "&pageno=" + str(page)
                html2 = url_open(url2)
                p = r'onclick="showdetail\(\'([^<]+\')'
                b = re.findall(p, html2)
                for j in b:
                    mark.append(j[0:32])
                child = re.findall(r'onclick="showchild\(\'([^<]+\')', html2)
                if (len(child) != 0):#存在有子项的权力清单
                    Child = list()
                    for k in range(0, len(child)):
                        url3 = "http://lz.gszwfw.gov.cn/gszw/qlqd/showchild.do?webid=" + city + "&maincode=" + child[k][0:5] + "&groupid=" + url[53:62] + "&type=" + i[0:2]
                        html3 = url_open(url3)
                        p = r'onclick="showdetail\(\'([^<]+\')'
                        b = re.findall(p, html3)
                        for j in b:
                            mark.append(j[0:32])
            print("mark_counts = ",len(mark))
        if "showggfw" in html:  #是否存在公共服务
            url3 = "http://lz.gszwfw.gov.cn/gszw/ggfwnew/list.do?webid=" + city + "&groupid=" + url[53:62] + "&groupname=" + urllib.parse.quote(DN[url[53:62]])
            html3 = url_open(url3)
            if "承办机构" not in html3:  #是否存在实施依据
                page = re.findall(r'pagecount="[0-9]{1,2}', html3)
                page = int(page[0][11:len(page[0])])
                for page in range(1, page + 1):
                    url2 = url3 + "&" + str(page)
                    html2 = url_open(url2)
                    p = r'[0-9|a-z]{8}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{4}-[0-9|a-z]{12}'
                    b = re.findall(p, html2)
                    for j in b:
                        mark.append("+" + j + url[53:62])
                print("mark_counts = ", len(mark))
    #print(mark[0])
    return(mark)

def downtable(url,rightNo,city,citycode,DN):
    if url[0] != "+":
        url2 = "http://www.gszwfw.gov.cn/gszw/qlqd/showdetails.do?mark=" + url + "&webid=" + city
        html = url_open(url2)
        html = lxml.html.fromstring(html)
        data = html.cssselect('td')[0]
        point = data.text_content()
        x = point.replace(" ", "")
        x = x.replace("\r\n","")
        x = x.replace("\t","")
        table = list()
        table.append(x[:x.find("类\u3000\u3000别")])
        if "在线办理" in x:
            table.append(x[x.find("类\u3000\u3000别") + 4:x.find("在线办理")])
        elif "办事指南" in x:
            table.append(x[x.find("类\u3000\u3000别") + 4:x.find("办事指南")])
        else:
            table.append(x[x.find("类\u3000\u3000别") + 4:x.find("承办机构")])
        table.append(x[x.find("承办机构")+4:x.find("实施依据")])
        table.append(x[x.find("实施依据")+4:x.find("实施主体")])
        table.append(x[x.find("实施主体")+4:x.find("责任事项")])
        competentDeptName = DN[url[12:21]]
    else:
        url2 = "http://lz.gszwfw.gov.cn/gszw/ggfwnew/showDetailNew.do?groupid=" + url[len(url)-9:len(url)] + "&webid=" + city + "&ggid=" + url[1:37]
        html = url_open(url2)
        html = lxml.html.fromstring(html)
        data = html.cssselect('td')[0]
        point = data.text_content()
        x = point.replace(" ", "")
        x = x.replace("\r\n", "")
        x = x.replace("\t", "")
        table = list()
        table.append(x[:x.find("类\u3000\u3000别")])
        if "在线办理" in x:
            table.append(x[x.find("类\u3000\u3000别") + 4:x.find("在线办理")])
        elif "办事指南" in x:
            table.append(x[x.find("类\u3000\u3000别") + 4:x.find("办事指南")])
        else:
            table.append(x[x.find("类\u3000\u3000别") + 4:x.find("服务内容")])
        table.append(x[x.find("承办机构") + 4:x.find("实施依据")])
        table.append(x[x.find("实施依据") + 4:x.find("实施主体")])
        table.append(x[x.find("实施主体") + 4:])
        competentDeptName = DN[url[len(url)-9:len(url)]]
    try:
        caseDomainDescribe = requests.post('http://172.16.4.63:8080/intelligent/rightsApi/getCaseDomain',data = {'competentDeptName':DN[url[12:21]]}).json()['result']['industryShowName']
        caseDomain = requests.post('http://172.16.4.63:8080/intelligent/rightsApi/getCaseDomain',data = {'competentDeptName':DN[url[12:21]]}).json()['result']['industryName']
    except:
        caseDomain = ""
        caseDomainDescribe = ""
    if table[3] !="":
        dic = {
            "rightNo": rightNo,
            "rightName":table[0],
            "rightType":table[1],
            "projectDecomposition": "",
            "executorName": table[4],
            "competentDeptName": competentDeptName,
            "undertakingAgency": table[2],
            "jointImpDept": "",
            "timeLimit": "",
            "accessWay": "",
            "complaintTel": "",
            "undertakingUser": "",
            "consultationTel": "",
            "setBasisSummary": table[3],
            "setBasis": table[3],
            "feeBasis": "",
            "law": "",
            "article": "",
            "feeScale": "",
            "approveImpDoc": "",
            "cityCode": citycode,#######################################各市不同
            "geoname": "金昌市",
            "sourceUrl": url2,
            "caseDomain":caseDomain,
            "caseDomainDescribe":caseDomainDescribe,
            "basisSummaryDefinition":getbsd(table[3]),
            "uniqueId": requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getUniqid",  data = {'uniqueidStr':citycode + rightNo}).json()["result"]
        }
        return dic
    else:
        return 0

def getbsd(sbs):
    try:
        result_law = requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getLawInfo",data={"setBasisSummary": sbs})
    except:
        print("v p n   掉 了")
        time.sleep(120)
        result_law = requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getLawInfo",data={"setBasisSummary": sbs})
    result_law_j = result_law.json()
    result = list()
    if result_law_j["state"] ==1:
        for i in range(0,len(result_law_j["result"])):
            try:
                clause = result_law_j["result"][i]["articles"][0]["clause"]
            except IndexError:
                clause = ""
            try:
                content = result_law_j["result"][i]["articles"][0]["content"]
            except IndexError:
                content = ""
            try:
                law = result_law_j["result"][i]["lawName"]
            except :
                law = ""
            result.append(
                {
                    "clause":clause,
                    "law":law,
                    "content":content
                }
            )
    return result

def main(city,citycode):
    rightno = 1###计数器
    url = "http://www.gszwfw.gov.cn/gszw/qlqd/list.do?webid=" + city
    html = url_open(url)
    urllist = geturllist(html,city = city)
    os.chdir('C:/Users/lenovo/Desktop/')
    print(urllist[1])
    with open(city + ".json", 'w', encoding='utf-8') as json_file:
        json_file.write("[")
        for aa in urllist[0]:
            mark = getmark([aa],city = city,DN = urllist[1])
            name = urllist[1][aa[53:62]]
            print(name,"\n",urllist[0].index(aa),"    to    ",len(urllist[0]))
            for i in range(0, len(mark)):
                try:
                    table = downtable(mark[i], str(rightno),city = city,citycode = citycode,DN = urllist[1])
                except:
                    print("IP可能封了，手动换个IP试试，在此暂停一分钟。")
                    time.sleep(120)
                    table = downtable(mark[i], str(rightno),city =city,citycode = citycode,DN = urllist[1])
                if table != 0:
                    rightno += 1
                    json.dump(table, json_file)
                    json_file.write(",\n")
                    print(i, "    to    ", len(mark))
        json_file.write("{}\n]")
    json_file.close()

'''
a =["http://lz.gszwfw.gov.cn/gszw/qlqd/showtop.do?webid=4&groupid=013899414&groupname=%E5%B8%82%E6%B0%91%E6%94%BF%E5%B1%80"]
mark = getmark(a)
os.chdir('C:/Users/lenovo/Desktop/')
with open("./hmm.json",'w',encoding='utf-8') as json_file:
    for i in range(0,len(mark)):
        table = downtable(mark[i],str(i+1))
        json.dump(table, json_file)
        json_file.write("\n")
        print(i,"    to    ",len(mark))
json_file.close()


url = "http://www.gszwfw.gov.cn/gszw/qlqd/list.do?webid=4"
html = url_open(url)
urllist = geturllist(html)
'''

#if __name__ == '__main__':
#    main(city = "7",citycode = "620300")
#a = "http://lz.gszwfw.gov.cn/gszw/qlqd/showtop.do?webid=4&groupid=013898200&groupname=%E5%B8%82%E5%85%AC%E5%AE%89%E5%B1%80"
#getmark([a])
'''
os.chdir('C:/Users/lenovo/Desktop/')
with open("微信.json", encoding='utf-8') as f:
	table = json.load(f)
f.close()
with open("urllist.json", encoding='utf-8') as f:
    urllist = json.load(f)
f.close()
with open("微信消息.json", 'w', encoding='utf-8') as json_file:
    json_file.write("[\n")
    for i in range(len(urllist)):
        html = table[i]["html"]
        while "<" in html:
            start = re.search(r'<[^>]+>',html).start()
            end = re.search(r'<[^>]+>',html).end()
            html = html[:start]+html[end:]
        try:
            a = requests.post("http://172.16.4.63:8080/intelligent/getProperty", data={"data": json.dumps({
                "caseName": table[i]['title'],
                "content": html,
                "caseDataType": "caseDataType_1"
            })}).json()
            domain = a['result']['recommendedCaseType'][0]['territory']
            mainType = a['resylt']['recommendedCaseType'][0]['industry']
            caseType = a['result']['recommendedCaseType'][0]['name']
        except:
            domain = ''
            mainType = ''
            caseType = ''
        print(i)
        dic = {
            'uniqld':get_uniqueid(urllist[i]),
            'sourceUrl':urllist[i],
            'title':table[i]['title'],
            'content':table[i]['html'],
            'releaseDepartment':table[i]['unit'],
            'relaseData':table[i]['time'],
            'category':"CaseAnalysis",
            'domain':domain,
            'mainType':mainType,
            'caseType':caseType,
            'cityCode':getcitycode(table[i]['unit']),
            'special':"",
            'creatUser':"guanyh",
            'creatTime':"2018年7月21日",
            'updateUser':"guanyh",
            'updateTime':"2018年7月21日"
        }
        json.dump(dic,json_file)
        json_file.write(",\n")
    json_file.write('""\n')
'''

'''
with open("重庆7_8.json", 'w', encoding='utf-8') as json_file:
    json_file.write("[\n")
    for i in range(len(table)):
        table[i]["uniqueId"] = requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getUniqid",  data = {'uniqueidStr':"620000" + str(i+1)}).json()["result"]
        table[i]["cityCode"] = "620000"
        json.dump(table[i],json_file)
        json_file.write(",\n")
        print(i)
    json_file.write("{}\n]")
json_file.close()
'''
"""
with open("gs权力清单.json", 'w', encoding='utf-8') as json_file:
    json_file.write("[\n")
    for i in range(len(table)):
        table[i]["uniqueId"] = requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getUniqid",  data = {'uniqueidStr':"620000" + str(i+1)}).json()["result"]
        table[i]["cityCode"] = "620000"
        json.dump(table[i],json_file)
        json_file.write(",\n")
        print(i)
    json_file.write("{}\n]")
json_file.close()
"""
'''
rootdir = 'C:/Users/lenovo/Desktop/list/'
list = os.listdir(rootdir) #列出文件夹下所有的目录与文件
for i in range(0,len(list)):
    path = os.path.join(rootdir,list[i])
    if os.path.isfile(path):
'''

os.chdir('C:/Users/lenovo/Desktop/')
with open("微信消息1.json", encoding='utf-8') as f:
	table = json.load(f)
f.close()
for i in table[:]:
    html = i["content"]
    while "<" in html:
        start = re.search(r'<[^>]+>', html).start()
        end = re.search(r'<[^>]+>', html).end()
        html = html[:start] + html[end:]
    try:
        a = requests.post("http://172.16.4.63:8080/intelligent/getProperty", data={"data": json.dumps({
            "caseName": i['title'],
            "content": html,
            "caseDataType": "caseDataType_1"
        })}).json()
    except:
        print("输入有问题")
    try:
        domain = a['result']['recommendedCaseType'][0]['territory']
        print(1)
        mainType = a['result']['recommendedCaseType'][0]['industry']
        caseType = a['result']['recommendedCaseType'][0]['name']
    except:
        domain = ''
        mainType = ''
        caseType = ''
        print("返回为空")
    i["domain"] = domain
    i['mainType'] = mainType
    i["caseType"] = caseType
with open("微信消息.json", 'w', encoding='utf-8') as json_file:
    json.dump(table,json_file)