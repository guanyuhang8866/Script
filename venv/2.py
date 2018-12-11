import json
import os
import requests
import time


path = r'C:/Users/lenovo/Desktop/大东/投诉13/'
for name in os.listdir(path):
    os.chdir('C:/Users/lenovo/Desktop/大东/投诉13/')
    with open(name, encoding='utf-8') as f:
        table = json.load(f)
    f.close()
    l = len(table)
    print(l)
    uniqid = list()
    id = list()
    for i in range(len(table)):
        if table[i]['sourceUrl'] not in uniqid:
            uniqid.append(table[i]['uniqid'])
            iscase = requests.post("http://172.16.4.63:8080/intelligent/caseType/rti",data ={"text" : table[i]['content']}).json()['resultState']
            if iscase:
                table[i]["isCase"] = 1
            else:
                table[i]["isCase"] = 0
        else:
            id.append(i)
        print(i ,'to',l)
    id = list(reversed(id))
    for j in id:
        del table[j]
    print(len(id))
    os.chdir('C:/User/lenovo/Desktop/投诉结果文档/')
    with open(name, 'w', encoding='utf-8') as json_file:
        json.dump(table,json_file)
    print(name)