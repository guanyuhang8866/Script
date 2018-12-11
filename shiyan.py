import urllib.request

import urllib

import re

import os


def url_open(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36")
    rep = urllib.request.urlopen(url)
    html = rep.read()
    # html = zlib.decompress(html ,16+zlib.MAX_WBITS)
    return html


def find_imag(html):
    p = r'<img src="([^"]+\.jpg)"'
    imglist = re.findall(p, html)
    return (imglist)


def save_imag(imaglist):
    for url in imaglist:
        html = url_open(url)
        name = url.split("/")[-1]
        with open(name, "wb") as p:
            p.write(html)


def id_trans(old_id):
    new_id = []
    for i in old_id:
        t = re.search(r'/t/', i)
        if t != None:
            a = t.start()
            b = t.end()
            new_id.append(i[:a] + "/pre/" + i[b:])
    return (new_id)


'''
#os.chdir('C:/Users/lenovo/Desktop/')
#os.mkdir("sdsd")
os.chdir('C:/Users/lenovo/Desktop/' + "ddd")
for i in range(7,10):
    url = "http://www.umei.cc/meinvtupian/"+str(i)+".htm"
    html = url_open(url)
    html = html.decode()
    imglist = find_imag(html)
    save_imag(imglist)
'''


def find_pictures(key, page):
    key_word = urllib.parse.quote(str(key))
    os.chdir('C:/Users/lenovo/Desktop/')
    os.mkdir(key)
    os.chdir('C:/Users/lenovo/Desktop/' + key)
    for i in range(pages):
        url = "http://www.ivsky.com/search.php?q=" + key_word + "&PageNo=" + str(i + 1)
        html = url_open(url)
        html = html.decode()
        imglist = find_imag(html)
        new_imglist = id_trans(imglist)
        save_imag(new_imglist)


key_word0 = input("请输入要查找的图片关键字：")
pages = int(input("请输入要保存图片的页数："))
find_pictures(key=key_word0, page=pages)

