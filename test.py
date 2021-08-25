from mysql.connector import cursor
from bs4 import BeautifulSoup
import mysql.connector as SqlCon
import requests
from utils import timer, time_diff
import json


def get_entities(host):
  title_list_in_db = []
  url_list_in_db = []

  entities = []
  header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

  response = requests.get(host, header)
  soup = BeautifulSoup(response.text, 'html.parser')

  div_main_mul = soup.find_all('div', {'class':['NiLAwe mi8Lec gAl5If jVwmLb Oc0wGc R7GTQ keNKEd j7vNaf nID9nc', 'NiLAwe mi8Lec gAl5If Oc0wGc R7GTQ keNKEd j7vNaf nID9nc sMVRZe']})

  div_main_one = soup.find_all('div', {'class':'NiLAwe y6IFtc R7GTQ keNKEd j7vNaf nID9nc'})

  print(len(div_main_mul) + len(div_main_one))
  
  for item in div_main_mul:
    # more than one publisher
    # entity = get_main_article(item)
    main_article = get_main_article(item)
    publisher = get_publisher(main_article)
    time_published = get_time_published(main_article)

    if check_nzh_stuff(publisher):
      # publisher is nzh or stuff
      if time_diff(time_published) <= 120:
        #if the published time is greater than 12 hours, then drop it
        entity = get_main_article_details(header, main_article, publisher, title_list_in_db, url_list_in_db)
        print(entity['news_title'], '    ', entity['news_publisher'])
        entities.append(entity)
      else:
        print('=========================')
        entity = get_main_article_details(header, main_article, publisher, title_list_in_db, url_list_in_db)
        print(entity['=news_title'], '    ', entity['news_publisher='])
        print('=too old=')
        print('=========================')
        
    else:
      # publisher is not nzh or stuff
      print('!nzh or stuff')
      sub_articles = get_sub_list(item)
      for sub_article in sub_articles:
        publisher = get_publisher(sub_article)
        sub_time_published = get_time_published(sub_article)

        if check_nzh_stuff(publisher):
          print('in')
        # publisher is nzh or stuff
          if time_diff(sub_time_published) <= 120:
            print('new ')
            #if the published time is greater than 12 hours, then drop it
            entity = get_sub_article_details(header, sub_article, publisher, title_list_in_db, url_list_in_db)
            print('@@@@@', entity['news_title'], '    ', entity['news_publisher'])
            entities.append(entity)
          else:
            print('&&&&&&&&&&&&&&&&&&&&&&&&&')
            entity = get_sub_article_details(header, item, publisher, title_list_in_db, url_list_in_db)
            print(entity['&news_title'], '    ', entity['news_publisher&'])
            print('&too old&')
            print('&&&&&&&&&&&&&&&&&&&&&&&&&')
          break
        
  for item in div_main_one:
    # only one publisher
    main_article = get_main_article(item)
    publisher = get_publisher(main_article)
    time_published = get_time_published(main_article)

    if check_nzh_stuff(publisher):
      # publisher is nzh or stuff
      if time_diff(time_published) <= 12:
        #if the published time is greater than 12 hours, then drop it
        entity = get_main_article_details(header, main_article, publisher, title_list_in_db, url_list_in_db)
        entities.append(entity)
  
  return entities       

def check_nzh_stuff(publisher):
  '''
  @description: check whether the news publisher is new zealand herald or not
  @param { publisher }
  @return { True or False } 
  '''
  flag = (str(publisher) == 'New Zealand Herald') or (str(publisher) == 'Stuff.co.nz') 
  print(flag, '#######', publisher)
  return flag

def check_exist_in_db(entity, list_from_db):
  '''
  @description: check either news url or news title is already in the db
  @param { entity, list_from_db} 
  @return { True or False }
  '''
  return entity in list_from_db

def get_main_article(entity):
  '''
  @description: get the main article area by finding <article class="...">...</article>
  @param { entity }
  @return { content inside article }
  '''
  main_article = entity.find('article', {'class': 'MQsxIb xTewfe R7GTQ keNKEd j7vNaf Cc0Z5d EjqUne'})
  return main_article


def get_main_article_details(header, main_article, publisher, title_list_in_db, url_list_in_db):
  '''
  @description: get all the details of the paricular news
  @param { header, main_article, publisher, title_list_in_db, url_list_in_db } 
  @return { details of the news }
  '''
  print('test, test, test')
  news_title = get_news_title(main_article)
  google_url = 'https://news.google.com/' + main_article.find('h3').find('a')['href'].replace('./', '')
  if not check_exist_in_db(news_title, title_list_in_db):
    # news title not exist in db
    news_url = get_real_news_url(headers=header)(google_url)
    if not check_exist_in_db(news_url, url_list_in_db):
      # news url not exist in db
      news_content, post_date, article_imgs = get_news_content(header, news_url, publisher)
      entity = {
        'news_title': str(news_title),
        'news_publisher': str(publisher),
        'post_date': str(post_date),
        'news_url': str(news_url),
        'img_url': article_imgs,
        'news_content': str(news_content)
      }
      return entity


def get_sub_article_details(header, sub_article, publisher, title_list_in_db, url_list_in_db):
  '''
  @description: get all the details of the news which in the sub list
  @param { header, sub_article, publisher, title_list_in_db, url_list_in_db } 
  @return { details of the news }
  '''
  news_title = get_sub_news_title(sub_article)
  google_url = 'https://news.google.com/' + sub_article.find('h4').find('a')['href'].replace('./', '')
  if not check_exist_in_db(news_title, title_list_in_db):
    # news title not exist in db
    news_url = get_real_news_url(headers=header)(google_url)
    if not check_exist_in_db(news_url, url_list_in_db):
      # news url not exist in db
      news_content, post_date, article_imgs = get_news_content(header, news_url, publisher)
      print(news_content, post_date, article_imgs)
      entity = {
        'news_title': str(news_title),
        'news_publisher': str(publisher),
        'post_date': str(post_date),
        'news_url': str(news_url),
        'img_url': article_imgs,
        'news_content': str(news_content)
      }
      return entity

def get_publisher(entity):
  '''
  @description: get the news publisher
  @param { entity }
  @return { publisher's name }
  '''
  publisher = entity.find('a', {'class': 'wEwyrc AVN2gc uQIVzc Sksgp'}).text
  return publisher

def get_time_published(entity):
  '''
  @description: get when the news published
  @param { entity }
  @return { time published }
  '''
  time_published = entity.find('time', {'class': 'WW6dff uQIVzc Sksgp'})['datetime']
  return time_published
  
def get_sub_list(entity):
  '''
  @description: get sub article list if the main area has no nzh or stuff
  @param { entity }
  @return { sub article list }
  '''
  sub_articles = entity.find('div', {'SbNwzf eeoZZ'}).find_all('article', {'class':'MQsxIb xTewfe tXImLc R7GTQ keNKEd keNKEd dIehj EjqUne'})
  return sub_articles

def get_news_title(entity):
  '''
  @description: get news title
  @param { entity }
  @return { news title }
  '''
  news_title = entity.find('h3', {'class':'ipQwMb ekueJc RD0gLb'}).find('a').text
  return news_title

def get_sub_news_title(entity):
  '''
  @description: get news title within the sub article list
  @param { entity }
  @return { news title }
  '''
  sub_news_title = entity.find('h4', {'class': 'ipQwMb ekueJc RD0gLb'}).find('a').text
  return sub_news_title

def get_real_news_url(headers):
  '''
  @description: get the news real url
  @param { header; google_url }
  @return { news url }
  '''
  def request_google_url(google_url):
    response = requests.get(google_url, headers)
    return response.url
  return request_google_url


def get_news_content(headers, news_url, publisher):
  '''
  @description: get news content
  @param { headers, news_url, publisher }
  @return { news content }
  '''  
  if (str(publisher) == 'New Zealand Herald'):
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', publisher)
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', news_url)
    content, post_date, article_imgs = get_content_nzh(headers, news_url)
    return content, post_date, article_imgs
    
    
  elif (str(publisher) == 'Stuff.co.nz'):
    content = ''
    post_date = ''
    article_imgs = []
    return content, post_date, article_imgs
  else:
    pass

def get_content_nzh(headers, news_url):
  '''
  @description: get news content from new zealand herald
  @param { headers, news_url }
  @return { news content, post time article_imgs }
  '''
  article_imgs = []
  response = requests.get(news_url, headers)
  nzh = BeautifulSoup(response.text, 'html.parser')
  
  article_main = nzh.find('section', {'class':'article__main'})
  print(article_main)
  post_time = article_main.find('time', {'class':'meta-data__time-stamp'})
  print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', post_time.text)
  article_body = article_main.find('section', {'class':'article__body full-content article__content'})
  
  para = article_body.find_all('p', {'class':'', 'dir':None})
  article_media_div = article_body.find_all('div', {'class': 'article-media'})
  print(article_media_div)
  tmp = []
  for item in para:
    tmp.append(item.text)
  content = ' '.join(tmp)

  for img in article_media_div:
    article_img = img.find('img')
    article_img_description = img.find('figcaption').text
    article_media = {
      'article_img': str(article_img['data-srcset']).split(',')[-1],
      'article_img_description': article_img_description
    }
    article_imgs.append(article_media)

  return content, post_time.text, article_imgs

def get_content_stuff(headers, news_url):
  '''
  @description: get news content from stuff.co.nz
  @param { headers, news_url }
  @return { news content, post time }
  '''
  response = requests.get(news_url, headers)
  stuff = BeautifulSoup(response.text, 'html.parser')
  
  article_main = stuff.find('main', {'class':'sics-component__app__main'})
  author = article_main.find('span', {'class':'sics-component__byline__author'}).find('span').text
  post_time = article_main.find('span', {'class':'sics-component__byline__date'}).text
  


@timer
def main():
  host = 'https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR04wZDE5aUVnSmxiaWdBUAE?hl=en-NZ&gl=NZ&ceid=NZ%3Aen'
  res = get_entities(host=host)
  with open('test.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False)

# start the program
if __name__ == '__main__':
  main()