from urllib import request
import os
import time
import lxml
import lxml.html
import re
import json
import urllib.parse
from lxml import etree
import requests
import cssselect
from selenium import webdriver

def open_Explor():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    # options.add_argument('window-size=1200x600')
    #driver = webdriver.Chrome(chrome_options=options)
    driver = webdriver.Chrome()
    return driver

def url_open(url):
    res = request.Request(url)
    res.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134")
    try:
        html = request.urlopen(res,timeout = 60).read()
    except:
        html = request.urlopen(res,timeout = 60).read()
    return html

def main(file):
    with open("海口.json", encoding='utf-8') as f:
        table = json.load(f)
    f.close()
    for i in range(len(table)):
        url = "http://www.sczwfw.gov.cn/app/main?areaCode=510100000000&iframeUrlLo=workGuide/detail?id=" + table[i] + "%26shardKey=5101%26typeflag=3"
        html = url_open(url).decode()


rightType = ["行政许可","行政处罚","行政强制","行政征收","行政裁决","行政确认","行政给付","行政奖励","行政检查","其他行政权力"]
rightType_code = ["1A","1B","1C","1D","1E","1F","1G","1H","1I","1Z"]
dirver = open_Explor()
url = "http://www.sczwfw.gov.cn/app/main?areaCode=510100000000&iframeUrlLo=workGuide/detail?id=3784201184572399616%26shardKey=5101%26typeflag=3"
dirver.get(url)
dirver.switch_to_frame("mainSubframe")
html = dirver.page_source
print(html)
html = etree.HTML(html)
a = html.xpath('//*[@id="tab_sdyj"]/tfoot/tr')
for i in range(len(a)):
    print(html.xpath('//*[@id="tab_sdyj"]/tfoot/tr[' + str(i+1) + ']/td/text()'))

pass