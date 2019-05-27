# python3
# coding=utf-8
import requests
from bs4 import BeautifulSoup as BS
import re
import csv
import time

class Crawler():
  def __init__(self):
    self.total_per_category = 50 # how many index per category (20 articles per an index)
    self.category_urls = [] # all categories
    self.category_names = [] # all categories' name
    self.index_urls = []  # number of total_per_category of indexes
    self.article_urls = [] # all articles
    self.id = 1 # id's serial number
    self.error = 0
    # initialize the csv writer
    self.writer = csv.writer(open('data.csv', 'w'))
    self.writer.writerow(['id', 'category', 'words'])
  ##################################
  #             shared             #
  ##################################
  #
  # target : get requests of the url
  # return : response of requests
  # correct
  #
  def req(self, url):
    r = requests.get(url = url, cookies = {'over18':'1'})
    r = r.content.decode('utf8')
    return r
  ##################################
  #             start              #
  ##################################
  #
  # target : start crawling using thread
  # return : None
  # correct
  #
  def start(self):
    while True:
      try:
        self.get_category_urls()
        break
      except:
        print('category error\n')
        self.category_urls = []
        time.sleep(1)
    for category_index in range(len(self.category_urls)-1, len(self.category_urls)):
      while True:
        try:
          self.get_index_urls(self.category_urls[category_index])
          break
        except:
          print('index error\n')
          self.index_urls = []
          time.sleep(1)
      for index_url in self.index_urls:
        while True:
          try:
            self.get_article_urls(index_url)
            self.error = 0
            break
          except:
            self.error += 1
            if self.error > 5:
              break
            print('argicle error            count : {0}\n'.format(self.error))
            self.article_urls = []
            time.sleep(1)
        for article_url in self.article_urls:
          while True:
            try:
              article = self.get_article(article_url)
              data = self.handle_article(article)
              split_data = self.split_article(data)
              self.write_into_csv(self.category_names[category_index], split_data)
              self.error = 0
              break
            except:
              self.error += 1
              if self.error > 5:
                break
              print('data handle error            count : {0}\n'.format(self.error))
              time.sleep(1)
      self.index_urls = []
      self.article_urls = []

  ##################################
  #              url               #
  ##################################
  #
  # target : get category pages from ptt homepage
  # return : an array containing category pages of ptt homepage
  # correct
  #
  def get_category_urls(self):
    r = self.req('https://www.ptt.cc/bbs/index.html')
    soup = BS(r, 'lxml')
    urls = soup.select('.board')
    for url in urls:
      self.category_names.append(url.select('.board-name')[0].string)
      self.category_urls.append('https://www.ptt.cc{0}'.format(url.attrs['href']))
    return self.category_urls
  #
  # target : get index pages from a category
  # return : an array containing index pages of category
  # correct
  #
  def get_index_urls(self, category_url):
    r = self.req(category_url)
    soup = BS(r, 'lxml')
    soup = soup.select('#action-bar-container')[0]
    urls = soup.findAll('a')
    for url in urls:
      if str('上頁') in url.string:
        prefix = url.attrs['href'].split('index')[0]
        newest = int(url.attrs['href'].split('index')[1].split('.h')[0]) + 1
        for index in range(newest - self.total_per_category, newest):
          self.index_urls.append('https://www.ptt.cc{0}{1}'.format(prefix, 'index{0}.html'.format(str(index))))
    return self.index_urls
  #
  # target : get all urls from a index page
  # return : an array containing a index page of urls
  # correct
  #
  def get_article_urls(self, index_url):
    r = self.req(index_url)
    soup = BS(r, 'lxml')
    soup = soup.select('.r-list-container')[0]
    urls = soup.findAll('a')
    for url in urls:
      if str('搜尋同標題文章') not in url.string and url.string[:5] != str('搜尋看板內'):
        self.article_urls.append('https://www.ptt.cc{0}'.format(url.attrs['href']))
    return self.article_urls
  ##################################
  #            article             #
  ##################################
  # 
  # target : get the title and content from ptt article
  # return : article 
  # correct
  #
  def get_article(self, article_url):
    r = self.req(article_url)
    soup = BS(r, 'lxml')
    title = soup.title.string
    title = title.split(' - ')[0]
    content = soup.select('#main-content')[0]
    content = str(content).split('\n\n--')[0]
    article = title + content
    return article
  #
  # target : just leave the article containing Chinese words
  # return : article having only Chinese words
  # correct
  #
  def handle_article(self, article):
    rule = re.compile('[^\u4e00-\u9fa5]')
    return rule.sub('', article)
  #
  # target : split the article to 1 word, 2 words, 3 words, and 4 words
  # return : an array containing words
  # correct
  #
  def split_article(self, data):
    split_data = []
    for i in range(len(data)):
      split_data.append(data[i])
      if i+1 < len(data):split_data.append(data[i:i+1+1])
      if i+2 < len(data):split_data.append(data[i:i+2+1])
      if i+3 < len(data):split_data.append(data[i:i+3+1])
    return split_data
  ##################################
  #              csv               #
  ##################################
  #
  # target : save the data into csv
  # return : None
  # correct
  #
  def write_into_csv(self, category_name, data):
    self.writer.writerow([self.id, category_name, data])
    self.id += 1
    

crawler = Crawler()
# print(crawler.split_article(crawler.handle_article(crawler.get_article('https://www.ptt.cc/bbs/sex/M.1558486609.A.126.html'))))
# print(crawler.split_article('我真的好愛好愛你'))
# crawler.get_urls('https://www.ptt.cc/bbs/sex/index4001.html')
# print(crawler.get_article_urls('https://www.ptt.cc/bbs/MLB/index1748.html'))
# print(crawler.get_index_urls('https://www.ptt.cc/bbs/NBA/index.html'))
# print(crawler.get_category_urls())
# crawler.write_into_csv('aaa', '123')
crawler.start()