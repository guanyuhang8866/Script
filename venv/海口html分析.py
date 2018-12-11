from urllib import request
import os
import time
import lxml
from lxml import etree
import lxml.html
import re
import json
from urllib.parse  import urljoin
from selenium import webdriver
import requests

zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

def zh_ex(word):
    global zh_pattern
    word = word.encode("utf8")
    match = zh_pattern.search(word)
    return match
def url_open(url):
    res = request.Request(url)
    res.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134")
    html = request.urlopen(res,timeout = 60).read()
    return html

def getbmName(url):
    htmlstr = url_open(url).decode("gbk")
    html = etree.HTML(htmlstr)
    url = html.xpath('//*[@id="dw_manage"]/ul/li/a/@href')
    bm = html.xpath('//*[@id="dw_manage"]/ul/li/a/text()')
    Url = list()
    for i in range(len(bm)):
        Url.append("http://www.haikou.gov.cn/zfdt/ztbd/2016nzt/qlzrqd" + url[i][1:])
    return [bm,Url]

def getpage(url):
    html = url_open(url).decode("gbk")
    html = etree.HTML(html)
    pagef = html.xpath('//*[@id="page_manage"]/script/text()')
    page = re.search(r'\([0-9]{1,3}',pagef[0]).group()[1:]
    pages = list()
    for i in range(int(page)):
        if i == 0:
            pages.append('index.html')
        else:
            pages.append('index_'+str(i)+'.html')
    return pages

def geturllist(urL):
    htmlstr = url_open(urL).decode("gbk")
    html = etree.HTML(htmlstr)
    url = html.xpath('//*[@id="sxlb_manage"]/ul/li/a/@href')
    Url = list()
    end = re.search(r'/index',urL).start()
    for i in range(len(url)):
        Url.append(urljoin(urL , url[i]))
    return Url
def getdata(url):
    htmlstr = url_open(url).decode("gbk")
    '''
    html = etree.HTML(htmlstr)
    data = list()
    data.append(html.xpath('//*[@id="content_k1"]/div[1]/div/table/tbody/tr[3]/td[1]/p/span/text()')[0])
    data.append(html.xpath('//*[@id="content_k1"]/div[1]/div/table/tbody/tr[3]/td[3]/p/span/text()')[0])
    data.append(html.xpath('//*[@id="content_k1"]/div[1]/div/table/tbody/tr[3]/td[6]/p/text()')[1])
    a = html.xpath('//*[@id="content_k1"]/div[1]/div/table/tbody/tr[3]/td[5]/p')
    law = ""
    for i in range(len(a)):
        print(html.xpath('//*[@id="content_k1"]/div[1]/div/table/tbody/tr[3]/td[5]/p['+ str(i+1) +']//span/text()')[:])
        print("\n\n")
    data.append(law)
    for i in data:
        print(i)
    '''
    return(htmlstr)

def getbsd(sbs):
    try:
        result_law = requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getLawInfo",data={"setBasisSummary": sbs})
    except:
        print("v p n   掉 了")
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


def gettable(data,name,url):
    pass
def main():
    rightNo = 0
    os.chdir('C:/Users/Administrator/Desktop/海口/')
    with open("海口1.json","w",encoding = "utf-8") as json_file:
        json_file.write("[\n")
        url = "http://www.haikou.gov.cn/zfdt/ztbd/2016nzt/qlzrqd/"
        urllist = getbmName(url)
        for i in range(len(urllist[1])):
            page = getpage(urllist[1][i])
            for j in page:
                url2 = urllist[1][i] + j
                urllist2 = geturllist(url2)
                for k in range(len(urllist2)):
                    print(urllist2[k])
                    try:
                        data = getdata(urllist2[k])
                    except:
                        print("某原因漏了一个")
                    json.dump(data,json_file)
                    json_file.write(',\n')
                    json.dump(urllist2[k],json_file)
                    json_file.write(',\n')
                    rightNo+=1
                    print(rightNo)
                print("page",j,"   to   ",len(urllist))
            print(urllist[0][i],'   完成')
            json_file.write("' '\n]")




os.chdir('C:/Users/lenovo/Desktop/海口/')
with open("海口.json", encoding='utf-8') as f:
	table = json.load(f)
f.close()
with open("海口权力清单.json", 'w', encoding='utf-8') as json_file:
    rightNo = 0
    json_file.write("[\n")
    for i in range(0,len(table)):
        if i % 2 == 0:
            html = table[i]
            url = table[i + 1]
            print(url)
            html = lxml.html.fromstring(html)
            data = html.cssselect('td')
            if len(data) == 15:
                a = data[12].text_content()
                b = data[8].text_content()
                c = data[10].text_content()
                d =data[13].text_content()
                e = html.cssselect('a')[5].text_content()
                try:
                    caseDomainDescribe = requests.post('http://172.16.4.63:8080/intelligent/rightsApi/getCaseDomain',
                                                       data={'competentDeptName': e}).json()['result'][
                        'industryShowName']
                    caseDomain = requests.post('http://172.16.4.63:8080/intelligent/rightsApi/getCaseDomain',
                                               data={'competentDeptName': e}).json()['result'][
                        'industryName']
                except:
                    caseDomain = ""
                    caseDomainDescribe = ""
                if a != "":
                    dic = {
                        "rightNo": rightNo,
                        "rightName": c,
                        "rightType": b,
                        "projectDecomposition": "",
                        "executorName": d,
                        "competentDeptName": e,#####
                        "undertakingAgency": d,#主管部门
                        "jointImpDept": "",
                        "timeLimit": "",
                        "accessWay": "",
                        "complaintTel": "",
                        "undertakingUser": "",
                        "consultationTel": "",
                        "setBasisSummary": a,
                        "setBasis": a,
                        "feeBasis": "",
                        "law": "",
                        "article": "",
                        "feeScale": "",
                        "approveImpDoc": "",
                        "cityCode": '460100',  #######################################各市不同
                        "geoname": "海口市",
                        "sourceUrl": url,
                        "caseDomain": caseDomain,
                        "caseDomainDescribe": caseDomainDescribe,
                        "basisSummaryDefinition": getbsd(a),
                        "uniqueId": requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getUniqid",
                                                  data={'uniqueidStr': '450100' + str(rightNo)}).json()["result"]
                    }
                json.dump(dic, json_file)
                json_file.write(',\n')
            rightNo += 1
            print(rightNo)
    json_file.write("' '\n]")
