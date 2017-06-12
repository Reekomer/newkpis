# inside facebook project

import scrapy
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Basic Lists
listPage = []
listDates = []
listLinks = []
listTitle = []
listPostviews = []
listViews = []

# KPIs lists
listViews = []
listLikes = []
listShares = []
listComments = []
# api list
listWeb = []
listUrl = []

#needed to do not repeat the PUT method
i = 0

# api definition
apiurl = 'http://127.0.0.1:8000/home/publisher/'
resp = requests.get(apiurl)
'''
#for testing
try:
    for x, in range(0,100):
        if resp.json()[x]["link"] != "null":
            listUrl.append(resp.json()[x]["link"])
            info = {
                'id': resp.json()[x]["id"],
                'link': resp.json()[x]["link"]
            }
            listWeb.append(info)
except:
    print("Loop out of range or no link in DB")
'''
try:
    for x, y in enumerate(resp):
        if resp.json()[x]["link"] != "null":
            listUrl.append(resp.json()[x]["link"])
            info = {
                'id': resp.json()[x]["id"],
                'link': resp.json()[x]["link"]
            }
            listWeb.append(info)
except:
    print("Loop out of range or no link in DB")

attempts = 0


def init_driver():
    driver = webdriver.PhantomJS()
    driver.wait = WebDriverWait(driver, 5)
    return driver

# Look for the elements to enable the program to connect to Facebook


def lookup(driver, email, password):
    driver.get("https://www.facebook.com")
    try:
        box1 = driver.wait.until(EC.presence_of_element_located(
            (By.NAME, "email")))
        box2 = driver.wait.until(EC.presence_of_element_located(
            (By.NAME, "pass")))
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.ID, "loginbutton")))
        box1.send_keys(email)
        box2.send_keys(password)
        button.click()
    except TimeoutException:
        print("Box or Button not found in facebook.com")

# Define the items to crawl


class Video(scrapy.Item):
    pagename = scrapy.Field()
    views = scrapy.Field()
    link = scrapy.Field()

# Define the behavior of the spider


class ProductSpider(scrapy.Spider):
    
    name = "updateData"
    allowed_domains = ['facebook.com']
    #start_urls = listUrl
    # for testing>
    start_urls = ['https://www.facebook.com/thebrblife/videos/617108691821692/','https://www.facebook.com/thebrblife/videos/617046805161214/']
# Connect to Facebook
    driver = init_driver()
    lookup(driver, "jeremy@stoyomedia.com", "Bouffegratos12")
    time.sleep(5)

    def __init__(self):
        self.driver

    def parse(self, response):
        self.driver.get(response.url)
        video = Video()
        global i

        title = self.driver.find_element_by_xpath('//title').text

        views = self.driver.find_element_by_xpath(
            '//div["_1t6k"][1]/span[@class="fcg"]').text

        # print title
        # print postviews
        # print views
        # print likes
        #date = self.driver.find_element_by_xpath('//span[@class="timestampContent"]').text
        # listDates.append((date).encode("utf-8"))

        elements = self.driver.find_elements_by_xpath(
            '//span[@class="fsm fwn fcg"]/a')
        for element in elements:
            try:
                listLinks.append(
                    (element.get_attribute('href')).encode("utf-8"))
            except:
                listLinks.append("empty")
            try:
                listDates.append((element.text).encode("utf-8"))
            except:
                listDates.append("empty")
            try:
                listTitle.append((title).encode("utf-8"))
            except:
                listTitle.append("empty")
            try:
                views = int((self.driver.find_element_by_xpath(
                    '//div[@class="_sa_ _gsd _5vsi _192z"]/div[@class="_1t6k"]/span').text).replace("k", "000").replace(" Views", "").replace(" View", ""))
                listViews.append(views)
            except:
                listViews.append(0)

            try:
                postviews = self.driver.find_elements_by_xpath(
                    '//div[@class="_sa_ _4duv _gsd _5vsi _192z"]/div/span')
                listPostviews.append(
                    (post.get_attribute('data-tooltip-content')).encode("utf-8"))
            except:
                listPostviews.append(0)
            try:
                comments = int((self.driver.find_element_by_xpath(
                    '//div[@class="_5aj7"]/div/span/em').text).replace(" comments", "").replace(" comment", "").replace(",", ""))
                listComments.append(comments)
            except:
                listComments.append(0)
            try:
                likes = int((self.driver.find_element_by_xpath(
                    '//div[@class="_3t53 _4ar- _ipn"]/a/span[1]').text).replace(".", "").replace("k", "000"))
                listLikes.append(likes)
            except:
                listLikes.append(0)
            try:
                shares = int((self.driver.find_element_by_xpath(
                    '//div[@class="_5aj7"]/div/a/em').text).replace(" shares", "").replace(" share", "").replace(",", ""))
                listShares.append(shares)
            except:
                listShares.append(0)

        dataList = []
        for w in range(0, len(listLinks)):
            dataInfo = {
                'link': listLinks[w],
                'views': listViews[w],
                'reactions': listLikes[w],
                'comments': listComments[w],
                'shares': listShares[w]
            }
            dataList.append(dataInfo)
        print "####################end of parse method########################"
# find out what is the DB id of the story to update
        for item in listWeb:
            for chunk in dataList:
                if item['link'] == chunk['link']:
                    chunk['id'] = item['id']
        print dataList
        for x in range(i, len(dataList)):
            url = apiurl + str(dataList[x]['id']) + "/"
            dataUpdated = {'views': dataList[x]['views'],
                           'likes': dataList[x]['reactions'],
                           'comments': dataList[x]['comments'],
                           'shares': dataList[x]['shares']
                           }
            resp = requests.put(url, data=dataUpdated)
            print('Interesting values: x= {} url ={}'.format(x, url))
            print dataUpdated
            print('Video updated. Name: {}'.format(resp.json()))
            i += 1


'''
        for x in range(0, len(dataList)):
            try:
                url = apiurl + str(dataList[x]['id']) + "/"
                dataUpdated = {'views': dataList[x]['views'],
                               'likes': dataList[x]['likes'], 
                               'comments': dataList[x]['comments'], 
                               'shares': dataList[x]['shares']}
                resp = requests.put(url, data= dataUpdated)
                print('Video updated. Name: {}'.format(resp.json()))
                print url

            except:
                print("Couldnt update")
'''