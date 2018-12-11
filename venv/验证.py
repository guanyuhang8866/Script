from urllib import request
import requests
import urllib
import re
import lxml.html
import cssselect as css
import pandas as pd
import os
import json
import time
from random import shuffle

def url_open(url):

    res = request.Request(url)
    res.add_header("User-Agent",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134")
    html = request.urlopen(res,timeout = 7).read().decode()
    return html

def geturllist(html):
    url = list()
    p = r'dept.{1,2}" ougrcode="([^<]+class)'
    data = re.findall(p,html)
    for i in data:
        a = i[0:9]
        b = i[17:len(i)-7]
        b = urllib.parse.quote(str(b))
        url.append("http://lz.gszwfw.gov.cn/gszw/qlqd/showtop.do?webid=4&groupid=" + a + "&groupname=" + b)
    return(url)

def getmark(urllist):
    mark = list()
    for url in urllist:
        html = url_open(url)
        p = r'onclick="showdown\(\'([^<]+\')'
        a = re.findall(p,html)
        t = int(len(a)/2)
        a = a[0:t]
        order = range(0,len(a))
        order = list(order)
        log = 1
        while log:
            shuffle(order)
            url2 = "http://lz.gszwfw.gov.cn/gszw/qlqd/showdown.do?webid=4&groupid=" + url[61:70] + "&type=" + a[order[0]][0:2]
            html2 = url_open(url2)
            p = r'onclick="showdetail\(\'([^<]+\')'
            b = re.findall(p, html2)
            if len(b) != 0:
                log = 0
            else:
                print("存在全部有子项的页面")
        for i in order:
            url2 = "http://lz.gszwfw.gov.cn/gszw/qlqd/showdown.do?webid=4&groupid="+url[61:70] +"&type="+a[i][0:2]
            html2 = url_open(url2)
            page = re.findall(r'pagecount="[0-9]{1,2}',html2)
            if len(page) == 0:#不用翻页
                p = r'onclick="showdetail\(\'([^<]+\')'
                b = re.findall(p,html2)
                for j in b:
                    mark.append(j[0:32] + url[61:70])
                child = re.findall(r'onclick="showchild\(\'([^<]+\')', html2)
                if (len(child) != 0):#存在有子项的权力清单
                    k0 = mark[-1][0:24]
                    Child = list()
                    Count = list()
                    count = re.findall(r'子项数：[0-9]{1,3}', html2)
                    for k in range(0, len(count)):
                        Child.append(child[k][0:5])
                        Count.append(count[k][4:len(count[k])])
                    for k1 in Child:
                        for k2 in range(0, len(Count)):
                            mark.append(k0 + k1 + str((k2+1)).zfill(3) + url[61:70])
            else: #政府部门的权利清单超过一页
                page = int(page[0][11:len(page[0])])
                for page in range(1,page+1):
                    url2 = "http://lz.gszwfw.gov.cn/gszw/qlqd/showdown.do?webid=4&groupid=" + url[61:70] + "&type=" + a[i][0:2] + "&pageno=" + str(page)
                    html2 = url_open(url2)
                    p = r'onclick="showdetail\(\'([^<]+\')'
                    b = re.findall(p, html2)
                    for j in b:
                        mark.append(j[0:32] + url[61:70])
                    child = re.findall(r'onclick="showchild\(\'([^<]+\')', html2)
                    if (len(child) != 0):#存在有子项的权力清单
                        k0 = mark[-1][0:24]
                        Child = list()
                        Count = list()
                        count = re.findall(r'子项数：[0-9]{1,3}', html2)
                        for k in range(0, len(count)):
                            Child.append(child[k][0:5])
                            Count.append(count[k][4:len(count[k])])
                        for k1 in Child:
                            for k2 in range(0, int(Count[Child.index(k1)])):
                                mark.append(k0 + k1 + str((k2 + 1)).zfill(3) + url[61:70])
            print("mark_counts = ",len(mark))
    #print(mark[0])
    return(mark)

def downtable(url,rightNo):
    url2 = "http://www.gszwfw.gov.cn/gszw/qlqd/showdetails.do?mark=" + url[0:32] + "&webid=4"
    html = url_open(url2)
    html = lxml.html.fromstring(html)
    data = html.cssselect('td')[0]
    point = data.text_content()
    x = point.replace(" ", "")
    x = x.split("\r\n")
    table = list()
    for i in x:
        if i != "":
            table.append(i)
    if table[3] == '\t':  #存在在线办理按钮 导致表格内容变多，处理办法。
        table.pop(3)
        table.pop(3)
        table.pop(3)
        table.pop(3)
        table.pop(3)
    #for i in table:
       # print(i)
    if(len(table)>=15):
        law = table[7]
        for i in range(8,table.index("实施主体")):
            law = law + table[i]
        print(len(table))
        print(url)
        try:
            caseDomainDescribe = requests.post('http://172.16.4.63:8080/intelligent/rightsApi/getCaseDomain',data = {'competentDeptName':getcompetentDeptName(url[32:41])}).json()['result']['industryShowName']
            caseDomain = requests.post('http://172.16.4.63:8080/intelligent/rightsApi/getCaseDomain',data = {'competentDeptName':getcompetentDeptName(url[32:41])}).json()['result']['industryName']
        except:
            caseDomain = ""
            caseDomainDescribe = ""
        dic = {
        "rightNo": rightNo,
        "rightName":table[0],
        "rightType":table[2],
        "projectDecomposition": "",
        "executorName": table[table.index("实施主体")+1],
        "competentDeptName": getcompetentDeptName(url[32:41]),
        "undertakingAgency": "",
        "jointImpDept": "",
        "timeLimit": "",
        "accessWay": "",
        "complaintTel": "",
        "undertakingUser": table[5],
        "consultationTel": "",
        "setBasisSummary": law,
        "setBasis": law,
        "feeBasis": "",
        "law": "",
        "article": "",
        "feeScale": "",
        "approveImpDoc": "",
        "cityCode": "620100",
        "geoname": "兰州市",
        "sourceUrl": "http://www.gszwfw.gov.cn/gszw/qlqd/showdetails.do?mark=" + url[0:32] + "&webid=4",
        "caseDomain":caseDomain,
        "caseDomainDescribe":caseDomainDescribe,
        "basisSummaryDefinition":getbsd(law),
        "uniqueId": requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getUniqid",  data = {'uniqueidStr':"620100" +rightNo}).json()["result"]
        }
    else:
        dic = 0
    return dic

def getbsd(sbs):
    result_law = requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getLawInfo",data={"setBasisSummary": sbs})
    result_law_j = result_law.json()
    result = list()
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

def getcompetentDeptName(code):
    dic = {
    "013898147": "市政府办公厅",
    "013898155": "市发改委",
    "01389842X": "市教育局",
    "01389818X": "市科技局",
    "013898163": "市工信委",
    "013898286": "市民宗委",
    "013898200": "市公安局",
    "013899414": "市民政局",
    "013898235": "市司法局",
    "013898243": "市财政局",
    "01389957X": "市人社局",
    "773448405": "市国土局",
    "013898534": "市环保局",
    "013898278": "市建设局",
    "773448413": "市规划局",
    "013898577": "市房产局",
    "767740813": "市城管委",
    "013898331": "市交通委",
    "73961107X": "市政府国资委",
    "01389834X": "市水务局",
    "013898673": "市农委",
    "013898366": "市生态局",
    "013898227": "市商务局",
    "013898067": "市物价局",
    "013898438": "市文旅局",
    "013898446": "市卫计委",
    "013898489": "市审计局",
    "013898593": "市政府外事办",
    "013898526": "市工商局",
    "013898518": "市质监局",
    "013898462": "市体育局",
    "720202516": "市安监局",
    "72020989X": "市食品药品监管局",
    "013898497": "市统计局",
    "013898403": "市粮食局",
    "739610851": "市经合局",
    "013899545": "市政府法制办",
    "013898657": "市信访局",
    "013899123": "市人防办",
    "55125594X": "市政府金融办",
    "438040082": "市两山指挥部",
    "013899326": "市地震局",
    "224394109": "市供销社",
    "438043865": "市公积金中心",
    "013899449": "市档案局",
    "013898024": "市残联",
    "224332944": "市烟草专卖局"}
    return(dic[code])

def main():
    rightno = 1###计数器
    url = "http://www.gszwfw.gov.cn/gszw/qlqd/list.do?webid=4"
    html = url_open(url)
    urllist = geturllist(html)
    os.chdir('C:/Users/lenovo/Desktop/')
    with open("兰州.json", 'w', encoding='utf-8') as json_file:
        json_file.write("[")
        for aa in urllist:
            mark = getmark([aa])
            name = getcompetentDeptName(aa[61:70])
            print(name,"\n",urllist.index(aa),"    to    ",len(urllist))
            for i in range(0, len(mark)):
                try:
                    table = downtable(mark[i], str(rightno))
                except:
                    print("IP可能封了，手动换个IP试试，在此暂停一分钟。")
                    time.sleep(10)
                    table = downtable(mark[i], str(rightno))
                if table != 0:
                    rightno += 1
                    json.dump(table, json_file)
                    json_file.write(",\n")
                    print(i, "    to    ", len(mark))
        json_file.write("]")
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
#   main()
#a = "http://lz.gszwfw.gov.cn/gszw/qlqd/showtop.do?webid=4&groupid=013898200&groupname=%E5%B8%82%E5%85%AC%E5%AE%89%E5%B1%80"
#getmark([a])
url = "https://image.baidu.com/search/detail?ct=503316480&z=0&ipn=d&word=selenium&step_word=&hs=0&pn=7&spn=0&di=146375280150&pi=0&rn=1&tn=baiduimagedetail&is=0%2C0&istype=0&ie=utf-8&oe=utf-8&in=&cl=2&lm=-1&st=undefined&cs=857804358%2C1124842279&os=3131868242%2C2387414333&simid=3514549598%2C148314882&adpicid=0&lpn=0&ln=1841&fr=&fmq=1536625763176_R&fm=&ic=undefined&s=undefined&se=&sme=&tab=0&width=undefined&height=undefined&face=undefined&ist=&jit=&cg=&bdtype=0&oriquery=&objurl=http%3A%2F%2Feasemod.osforce.cn%2Ffiles%2Fcourse%2F2014%2F11-25%2F1530080d4cdd555126.jpg%3Fosf_6.0.6&fromurl=ippr_z2C%24qAzdH3FAzdH3Fjwfj451_z%26e3B5fu56vj_z%26e3BvgAzdH3Fv576fjAzdH3Fdml&gsm=0&rpstart=0&rpnum=0&islist=&querylist="
html = url_open(url)
print (html)
print(type(html))
