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
from lxml import etree

def url_open(url):

    res = request.Request(url)
    res.add_header("User-Agent",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134")
    html = request.urlopen(res,timeout = 60).read().decode()
    return html

def main():
    os.chdir('C:/Users/lenovo/Desktop/')
    next = 1
    page = 1
    while next :
        url = "https://www.zhipin.com/c101020100-p100507/h_101020100/?query=BI&page="+ str(page) +"&ka=page-" + str(page)
        html = url_open(url)
        html = etree.HTML(html)
        urllist = html.xpath('//*[@id="main"]/div/div[2]/ul/li/div/div[1]/h3/a/@href')
        for i in urllist:
            url = "https://www.zhipin.com" + i
            html = url_open(url)
            html = etree.HTML(html)
            job_name = html.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div[2]/h1/text()')
            location = html.xpath('//*[@id="main"]/div[1]/div/div/div[2]/p/text()[1]')
            need1 = html.xpath('//*[@id="main"]/div[1]/div/div/div[2]/p/text()[2]')
            need2 = html.xpath('//*[@id="main"]/div[1]/div/div/div[2]/p/text()[3]')
            money = html.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div[2]/span/text()')
            where = html.xpath('//*[@id="main"]/div[1]/div/div/div[3]/h3/a/text()')
            do = html.xpath('//*[@id="main"]/div[1]/div/div/div[3]/p[1]/text()')
            detail = html.xpath('//*[@id="main"]/div[3]/div/div[2]/div[3]/div[1]/div/text()')
            print(job_name[0])
            print(location[0])
            for j in detail:
                print(j,"\n")
            next = 0

main()
