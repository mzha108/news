# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
import os
import re
import pyodbc
import mysql.connector
import time
import json
import datetime
from utils import timer




#file_path是access文件的绝对路径
file_path = r"C:\Users\Mu\Documents\workspaces\web\scrapy\scrapyProject\Database1.accdb"
#host是新闻速递首页的url
# host = 'https://www.6parknews.com/newspark/index.php?p=3'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
#local_path是抓取图片存储的根目录
local_path = r"C:\Users\Mu\Documents\workspaces\web\scrapy\scrapyProject\img_news"




def mkdir(path):
  """create directories to save images"""
  folder = os.path.exists(path)

  if not folder:
    os.makedirs(path)
    return True
  else:
    print('--- folder already exists ---')
    return False



def get_urls(host):
  url_list = []
  """从新闻速递首页获取文章URL"""
  response = requests.get(host, headers)  # 发起网络请求，获得响应
  soup = BeautifulSoup(response.text, 'html.parser') # 使用BeautifulSoup解析，查找想要的内容。html.parser是熊内置的解析方案，可以不填会有warning
  div_node = soup.find('div', {'id': 'd_list'})  # 查找id值为d_list的div标签，
  ul_node = div_node.find('ul')  # 在div标签下查找第一个ul标签
  for li_node in ul_node.findAll('li'):  # 使用find_all()找出所有<li>标签，在for循环中解析每个<li>标签
    href = li_node.find('a')['href']  # 打印出li标签链接（href属性的值）
    if 'newspark' in href:
      url_article = urljoin(response.url, href) # response.url是响应的地址，不一定是原始请求地址哦，因为网站可能会把对请求做重定向
      url_list.append(url_article)
  # print(url_list)
  f = open('log.txt','a', encoding='utf-8')
  print("本次抓取一共采集 "+str(len(url_list))+" 条数据", file=f)
  f.close()

  return url_list



def get_info(url):
  """get title, publish date, content, source, image of the article """
  response = requests.get(url, headers)  # 发起网络请求，获得响应
  response.encoding = 'utf-8'  # 网页编码
  soup = BeautifulSoup(response.text, 'html.parser')  # 使用BeautifulSoup解析，查找想要的内容。html.parser是熊内置的解析方案，可以不填会有warning
  title = soup.find('h2', {'style': 'margin:15px;text-align:center;'}).text.strip()
  sub_title = soup.find('p', {'style': 'padding:5px;'}).text.strip().replace('\r', '').replace('\n', '').replace('\t', '')
  source = "".join(re.findall(r'(\s+\D*\s+)于', sub_title)).strip()
  timestamp = "".join(re.findall(".*于(.*)大.*", sub_title)).strip()
  
  """内容包含正文以及视频链接"""
  content = get_vid_link(soup.find('div', {'id': 'shownewsc'}).findAll('iframe')) + soup.find('div', {'id': 'shownewsc'}).text.strip().replace("'","''")
  
  tmp =soup.find('div', {'id': 'shownewsc'}).findAll('img')
  img_url_list = []
  for i in tmp:
    # img_url_list.append(re.findall(r'http.*(?=")', str(i)))
    img_url_list.append(i.get('src'))
  img_url = ','.join(img_url_list)
  # print(img_url)
  f = open('log.txt', 'a', encoding = 'utf-8')
  print("数据保存成功", file=f)
  # print("'url': ",url, "'title': ",title, "'date_publish': ",timestamp, "source: ",source) ################ modified
  f.close()
  return {'url': url, 'title': title, 'date_publish': timestamp, 'content': content, 'source': source, 'img_url': img_url}


def get_vid_link(vid_links):
  video_links = ''
  if vid_links:
    for video in vid_links:
      video_src = video.get('src')
      video_links += video_src + '[v]'
  return video_links


def save_to_db(entities):
  '''
  Save data into MySql database
  
  param:
    entities: list of news with its info
    
  '''
  # prepare data to be saved into DB
  data = []
  
  for entity in entities:
    entity_dict = {
      "news_url": entity["url"],
      "news_title": entity["title"],
      "news_original_published": entity["date_publish"],
      "news_content": entity["content"],
      "modified_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "is_published": "0",
      "source": entity["source"],
      "genre": "int",
      "img_url": entity['img_url']
    }
    
    data.append(entity_dict)
    
  # database operation
  query = ("insert into newsdb.news" 
           "(news_url, news_title, news_original_published, news_content, modified_date, is_published, source, genre, img_url)"
           "values (%(news_url)s, %(news_title)s, %(news_original_published)s, %(news_content)s, %(modified_date)s, %(is_published)s, %(source)s, %(genre)s, %(img_url)s)")
  
  try:
    cnx = mysql.connector.connect(database='newsdb',
                                  user='root')
    cursor = cnx.cursor()
    
    try:
      cursor.executemany(query, data)
      cnx.commit()
    
      cursor.close()
      cnx.close()
    except Exception as e:
      print('Error: {0}. Please find more at https://mariadb.com/kb/en/mariadb-error-codes/'.format(e))
      
  except mysql.connector.Error as e:
    print('Error: {0}. Please find more at https://mariadb.com/kb/en/mariadb-error-codes/'.format(e))
  finally:
    print('Finished!')

@timer
def main():
  '''main function'''
  # count = 0
  info_list = []
  for page in range(1): # can set how many pages to view
    page += 1
    host = 'https://www.6parknews.com/newspark/index.php?p=%d' % (page)
    
    for url in get_urls(host):
      # count += 1
      info_list.append(get_info(url))
      # if (count>0):
      #   break
      
    save_to_db(info_list)

    # Save news as JSON file locally
    # with open('local.json', 'w', encoding='utf-8') as f:
    #   json.dump(info_list, f, ensure_ascii=False)
    
    info_list.clear()
  f = open('log.txt','a', encoding='utf-8')
  print("采集结束", file=f)
  f.close()

if __name__ == '__main__':
  main()
