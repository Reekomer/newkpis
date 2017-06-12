#inside facebook project

import scrapy
import time
import psycopg2
import json
import requests
from scrapy_djangoitem import DjangoItem
from home.models import Publisher
from scrapy_djangoitem import DjangoItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

#Connect to the DB
conn = psycopg2.connect(database="d22i0kdtb07bvn", user = "sdibkoceylgpfh", \
password = "f900a79d1cb634488d022b1cbb791dc41043390bde9c32eb81e10c03954c76d0", \
host = "ec2-54-228-255-234.eu-west-1.compute.amazonaws.com", port = "5432")

cur = conn.cursor()
cur.execute("SELECT * FROM public.stoyo_data1")
rows = cur.fetchall()

#define header
headers = {'content-type' : 'application/json'}

#define the API endpoint
video = 'http://127.0.0.1:8000/home/publisher/'

dbLinkList = []
i = cur.rowcount

for i in range(0,i):
    dbLinkList.append(rows[i][2])

listPage = []
listViews = []
listLinks = []
listTitle = []
listFinal = []
attempts = 0

def init_driver():
  driver = webdriver.Firefox()
  driver.wait = WebDriverWait(driver, 5)
  return driver

#Look for the elements to enable the program to connect to Facebook
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

#Define the items to crawl
class PublisherItem(DjangoItem):
    django_model = Publisher


#Define the behavior of the spider
class ProductSpider(scrapy.Spider):
  name = "dbcrawl"
  allowed_domains = ['facebook.com']
  f = open("pub.txt")
  start_urls = [url.strip() for url in f.readlines()]
#Connect to Facebook
  driver = init_driver()
  lookup(driver, "jeremy@stoyomedia.com", "Bouffegratos12")
  time.sleep(5)

  def __init__(self):
   self.driver

  def parse(self, response):
   self.driver.get(response.url)
   pub = PublisherItem()
   attemps = 0
   #50 attempts is 600 videos back. 60 seems to be optimal
   while attemps < 10:
    self.driver.implicitly_wait(10)

    try:
     self.driver.implicitly_wait(10)
     more = self.driver.find_element_by_xpath('//div[@class="_3v4j"]/div[@class="clearfix uiMorePager stat_elem _52jv"]')
     more.click()
     #print self.driver.find_element_by_xpath('//div[@class="_3v4h _50f3 _50f7"]/a/@href')
     attemps += 1
     #print attemps
    except:
      break
    #myfile = open('links.txt', 'w')
   page = self.driver.find_element_by_xpath('//title').text


   views = self.driver.find_elements_by_xpath('//div[@class="_u3y"]/div[@class="_3v4i"]/div[@class="fsm fwn fcg"]')

   elements = self.driver.find_elements_by_xpath('//div[@class="_u3y"]/div[@class="_3v4h _50f3 _50f7"]/a')
   print('Length of elements: {}'.format(len(elements)))

   for element in elements:
     try:
      listTitle.append((element.text).encode("utf-8"))
      listLinks.append((element.get_attribute('href')).encode("utf-8"))
      listPage.append((page).encode("utf-8"))
     except:
       print("Not conform")
   #save the list in the DB
   for i in range(0,len(listTitle)):
       info = {
         'title': listTitle[i],
         'link': listLinks[i],
         'page_name': listPage[i],
       }
       resp = requests.post(video,data=json.dumps(info), headers=headers)
       print('Video imported: {}'.format(resp))