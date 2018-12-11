import lxml
from lxml import etree
import json
import os
import requests
import time

def loadfile(filename):
    os.chdir('C:/Users/lenovo/Desktop/重庆/')
    with open(filename + '.json', encoding='utf-8') as f:
        table = json.load(f)
    f.close()
    return table

def TurnToThml(htmlstr):
    html = etree.HTML(htmlstr)
    result = etree.tostring(html)
    return html

def Todataframe(html):
    head = list()
    data = list()
    a = len(html.xpath('//*[@id="baseInfo"]/table/tbody/tr'))
    for i in range(a):
        b = html.xpath('//*[@id="baseInfo"]/table/tbody/tr[' + str(1 + i) + ']/td')
        c = html.xpath('//*[@id="baseInfo"]/table/tbody/tr[' + str(1 + i) + ']/th')
        for j in range(len(b)):
            head.append(c[j].text)
            data.append(b[j].text)
    result = dict(zip(head,data))
    return result

def To_set_basis(html):
    setBasis = ""
    setBasisSummary = ""
    s = len(html.xpath('//*[@id="approval_basis"]'))
    a = len(html.xpath('//*[@id="approval_basis"]/table/tbody/tr'))
    for i in range(int(a / s - 2)):
        b = html.xpath('//*[@id="approval_basis"]/table/tbody/tr[' + str(i + 2) + ']/td')
        if(s == 1):
            for j in range(len(b)):
                if (j < 3) & (b[j].text != "暂无"):
                    setBasis = setBasis + b[j].text + "  "
                if (j >= 3) & (b[j].text != "暂无"):
                    setBasisSummary = setBasisSummary + b[j].text + "  "
        if (s == 2):
            for j in range(len(b[:int(len(b)/2)])):
                if (j < 3) & (b[j].text !="暂无"):
                    setBasis = setBasis + b[j].text + "  "
                if (j >= 3):
                    setBasisSummary = setBasisSummary + b[j].text + "  "
    result = [setBasisSummary,setBasis]
    return result

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

def main(filename):
    rightNo = 1
    os.chdir('C:/Users/lenovo/Desktop/')
    with open("842445.json", 'w', encoding='utf-8') as json_file:
        json_file.write("[\n")
        for name in filename:
            print(name)
            table = loadfile(name)
            for i in range(len(table)):
                if i % 2 == 0:
                    html = TurnToThml(table[i])
                    data = Todataframe(html)
                    setBasis = To_set_basis(html)
                    url = table[i + 1]
                    try:
                        caseDomainDescribe = requests.post('http://172.16.4.63:8080/intelligent/rightsApi/getCaseDomain',
                                                           data={'competentDeptName': data['决定机构']}).json()['result'][
                            'industryShowName']
                        caseDomain = requests.post('http://172.16.4.63:8080/intelligent/rightsApi/getCaseDomain',
                                                   data={'competentDeptName': data['决定机构']}).json()['result']['industryName']
                    except:
                        caseDomain = ""
                        caseDomainDescribe = ""
                    ##########################不唯一的内容
                    dic = {
                        "rightNo": rightNo,
                        "rightName": data['事项名称'],
                        "rightType": data['事项类型'].replace(" ",'').replace("\n","").replace("\t",""),
                        "projectDecomposition": "",
                        "executorName": data['决定机构'],
                        "competentDeptName": data['决定机构'],
                        "undertakingAgency": '',
                        "jointImpDept": "",
                        "timeLimit": "",
                        "accessWay": "",
                        "complaintTel": "",
                        "undertakingUser": "",
                        "consultationTel": "",
                        "setBasisSummary": setBasis[0],
                        "setBasis": setBasis[1],
                        "feeBasis": "",
                        "law": "",
                        "article": "",
                        "feeScale": "",
                        "approveImpDoc": "",
                        "cityCode": "500000",  #######################################各市不同
                        "geoname": "重庆市",
                        "sourceUrl": url,
                        "caseDomain": caseDomain,
                        "caseDomainDescribe": caseDomainDescribe,
                        "basisSummaryDefinition": getbsd(setBasis),
                        "uniqueId": requests.post("http://172.16.4.63:8080/intelligent/rightsApi/getUniqid",
                                                  data={'uniqueidStr': "500000" + str(rightNo)}).json()["result"]
                    }
                    rightNo += 1
                    json.dump(dic, json_file)
                    json_file.write(",\n")
                    print(rightNo)
            json_file.write('" "\n]')
        pass


