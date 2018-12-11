from selenium import webdriver
import time

def download1(html):
    pass

def download2(html):
    pass
start =time.time()
table = list()
options = webdriver.ChromeOptions()
options.add_argument('headless')
# options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(chrome_options=options)
driver.get('http://zwfw.cq.gov.cn/icity/govservice/powerlist')
title = driver.window_handles
for k in title[1:]:
    driver.switch_to.window(k)
    driver.close()
driver.switch_to.window(driver.window_handles[0])
for i in range(1,4):
    child = driver.find_elements_by_class_name('qlqdtitle')
    print(len(child))
    for j in range(0,len(child)):
        child[j].click()
        if len(driver.window_handles)==1:
            continue
        title = driver.window_handles
        driver.switch_to.window(title[1])
        log = driver.find_elements_by_xpath("//*[@id='itemInfoDetail']/button")
        html_1 = driver.page_source
        type1 = "设定依据" in html_1
        type2 = "实施依据" in html_1
        if(len(log)!=0):
            log[0].click()
            driver.switch_to.window(driver.window_handles[-1])
            html_2 = driver.page_source
            type1 = "设定依据" in html_2
            type2 = "实施依据" in html_2
            if type1:
                table.append(download1(html_2))
                print("1")
            elif type2:
                table.append(download2(html_2))
                print("2")
        elif type1:
            table.append(download1(html_1))
            print("3")
        elif type2:
            table.append(download2(html_1))
            print("4")
        else:
            print("没戏唱")
        title = driver.window_handles
        for k in title[1:]:
            driver.switch_to.window(k)
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
    driver.switch_to.window(driver.window_handles[0])
    driver.find_element_by_xpath('//*[@id="laypage_0"]/a['+str(i)+']').click()
    print("page:",i,"   to   ","page:107")
end = time.time()
print('Running time: %s Seconds'%(end-start))
for i in range(4,108):
    child = driver.find_elements_by_class_name('qlqdtitle')
    print(len(child))
    for j in range(0,len(child)):
        child[j].click()
        if len(driver.window_handles)==1:
            continue
        title = driver.window_handles
        driver.switch_to.window(title[1])
        log = driver.find_elements_by_xpath("//*[@id='itemInfoDetail']/button")
        html_1 = driver.page_source
        type1 = "设定依据" in html_1
        type2 = "实施依据" in html_1
        if(len(log)!=0):
            log[0].click()
            driver.switch_to.window(driver.window_handles[-1])
            html_2 = driver.page_source
            type1 = "设定依据" in html_2
            type2 = "实施依据" in html_2
            if type1:
                table.append(download1(html_2))
                print("1")
            elif type2:
                table.append(download2(html_2))
                print("2")
        elif type1:
            table.append(download1(html_1))
            print("3")
        elif type2:
            table.append(download2(html_1))
            print("4")
        else:
            print("没戏唱")
        title = driver.window_handles
        for k in title[1:]:
            driver.switch_to.window(k)
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
    driver.switch_to.window(driver.window_handles[0])
    driver.find_element_by_xpath('//*[@id="laypage_0"]/a['+str(i)+']').click()
    print("page:",i,"   to   ","page:107")
