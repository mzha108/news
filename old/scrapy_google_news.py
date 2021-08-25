'''
Author: Mu
Date: 2021-07-19 13:32:52
LastEditors: Mu
LastEditTime: 2021-07-23 15:31:33
'''

from mysql.connector import cursor
from bs4 import BeautifulSoup
import mysql.connector as SqlCon
import requests
from utils import timer, time_diff


def get_entity(host, title_list_in_db, url_list_in_db):
  '''
  @description: 
  @param {(str) host, (str) title_list_in_db}
  @return {(list) entities}
  '''  
  entities = []
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
  
  response = requests.get(host, headers=headers)
  soup = BeautifulSoup(response.text, 'html.parser')
  
  div_main_mul = soup.find_all('div', {'class':'NiLAwe mi8Lec gAl5If jVwmLb Oc0wGc R7GTQ keNKEd j7vNaf nID9nc'})
  div_main_one = soup.find_all('div', {'class':'NiLAwe y6IFtc R7GTQ keNKEd j7vNaf nID9nc'})
  
  # if there are MORE THAN ONE news listed 
  for item in div_main_mul:
    article_main = item.find('article', {'class': 'MQsxIb xTewfe R7GTQ keNKEd j7vNaf Cc0Z5d EjqUne'})
    
    source = article_main.find('a', {'class': 'wEwyrc AVN2gc uQIVzc Sksgp'}).text
    time = article_main.find('time', {'class': 'WW6dff uQIVzc Sksgp'})['datetime']
    print('1. ',source)

    # if the publisher is not new zealand herald or stuff, then find the one in the sub-list
    if ((str(source) != 'New Zealand Herald') and (str(source) != 'Stuff.co.nz')):
      print('!nzh or stuff')
      # if the published time is greater than 12 hours, then drop it
      if time_diff(time) <= 12:
        print('published 12 hours ago.. too old...')
        sub_article = item.find('div', {'SbNwzf eeoZZ'}).find_all('article', {'class':'MQsxIb xTewfe tXImLc R7GTQ keNKEd keNKEd dIehj EjqUne'})
        print(len(sub_article))
        for sub_item in sub_article:
          source = sub_item.find('a', {'class': 'wEwyrc AVN2gc uQIVzc Sksgp'}).text
          print('2. ', source)
          if ((str(source) == 'New Zealand Herald') or (str(source) == 'Stuff.co.nz')):
            print('find nzh or stuff')
            title = sub_item.find('h4', {'class': 'ipQwMb ekueJc RD0gLb'}).find('a').text
            google_url = 'https://news.google.com/' + sub_item.find('h4').find('a')['href'].replace('./', '')
            print('2.1. ', source, '   ', title)
            if (title not in title_list_in_db or len(title_list_in_db) == 0):
              url = get_real_news_url(google_url, headers)

              # check url is already exist
              if (url not in url_list_in_db):
                entity = {
                  'news_url': str(url),
                  # 'news_original_published': str(),
                  'news_title': str(title),
                  # 'modified_date':'',
                  #'is_published': '',
                  'news_publisher': str(source)
                }
                entities.append(entity)
              
              # print(url)
            else:
              # print(title)
              pass
            break
          else:
            # source = article_main.find('a', {'class': 'wEwyrc AVN2gc uQIVzc Sksgp'}).text
            # title = article_main.find('h3', {'class':'ipQwMb ekueJc RD0gLb'}).find('a').text
            # google_url = 'https://news.google.com/' + article_main.find('h3').find('a')['href'].replace('./', '')
            # print('2.2. ', source, '   ', title)
            # if (title not in title_list_in_db or len(title_list_in_db) == 0):
            #   url = get_real_news_url(google_url, headers)
              
            #   entity = {
            #     'news_url': str(url),
            #     # 'news_original_published': str(),
            #     'news_title': str(title),
            #     # 'modified_date':'',
            #     #'is_published': '',
            #     'source': str(source)
            #   }
            #   entities.append(entity)
            #   # print(url)
            # else:
            #   # print(title)
            #   pass
            continue
      
    # the publisher is new zealand herald or stuff 
    else:

      # if the published time is greater than 12 hours, then drop it
      if time_diff(time) <= 12:
        title = article_main.find('h3', {'class':'ipQwMb ekueJc RD0gLb'}).find('a').text
        google_url = 'https://news.google.com/' + article_main.find('h3').find('a')['href'].replace('./', '')
        print('3. ', source, '   ', title)
        if (title not in title_list_in_db or len(title_list_in_db) == 0):
          url = get_real_news_url(google_url, headers)
          
          # check url is already exist
          if (url not in url_list_in_db):
            entity = {
              'news_url': str(url),
              # 'news_original_published': str(),
              'news_title': str(title),
              # 'modified_date':'',
              #'is_published': '',
              'news_publisher': str(source)
            }
            entities.append(entity)
            # print(url)
        else:
          # print(title)
          pass
      
  # if there is ONLY ONE news listed
  for item in div_main_one:
    article_main = item.find('article', {'class': 'MQsxIb xTewfe R7GTQ keNKEd j7vNaf Cc0Z5d EjqUne'})
    source = article_main.find('a', {'class': 'wEwyrc AVN2gc uQIVzc Sksgp'}).text
    title = article_main.find('h3', {'class':'ipQwMb ekueJc RD0gLb'}).find('a').text
    time = article_main.find('time', {'class': 'WW6dff uQIVzc Sksgp'})['datetime']
    google_url = 'https://news.google.com/' + article_main.find('h3').find('a')['href'].replace('./', '')
    print('3. ', source, '   ', title)
    if (title not in title_list_in_db or len(title_list_in_db) == 0):

      #if published time is greater than 12 hours, then drop it
      if time_diff(time) <= 12:
        url = get_real_news_url(google_url, headers)
        
        entity = {
          'news_url': str(url),
          # 'news_original_published': str(),
          'news_title': str(title),
          # 'modified_date':'',
          #'is_published': '',
          'news_publisher': str(source)
        }
        entities.append(entity)
      # print(url)
    else:
      # print(title)
      pass
  return entities


def get_news_content(url, headers, source):
  '''
  @description: 
  @param {*}
  @return {*}
  '''  
  if (str(source) == 'New Zealand Herald'):
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', source)
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', url)
    response = requests.get(url, headers=headers)
    nzh = BeautifulSoup(response.text, 'html.parser')
    
    article_main = nzh.find('section', {'class':'article__main'})
    # print(article_main)
    post_time = article_main.find('time', {'class':'meta-data__time-stamp'})
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@', post_time.text)
    article_body = article_main.find('section', {'class':'article__body full-content article__content'})
    # print(article_body)
    
    para = article_body.find_all('p', {'class':'', 'dir':None})
    
    
    # with open('test.txt', 'w', encoding='utf-8') as f:
    #   print(post_time.text, '            ', source, file=f)
    tmp = []
    for item in para:
      tmp.append(item.text)
    test = ' '
    print(test.join(tmp))
    
    
  elif (str(source) == 'Stuff.co.nz'):
    pass
  else:
    pass
 
  
  

  
def get_real_news_url(google_url, headers):
  # print(google_url)
  response = requests.get(google_url, headers)
  
  return response.url
  
def save_data_to_db(data):
  '''
  @description: 
  @param {*}
  @return {*}
  '''  
  
  # try:
  cnx = SqlCon.connect(database='newsdb',
                        user='root')
  cursor = cnx.cursor(named_tuple=True)
  
  query = ''' INSERT INTO `news_details_tbl`(`news_url`, `news_title`, `source`) VALUES (%(news_url)s, %(news_title)s, %(source)s) '''
  
  cursor.executemany(query, data)
  cnx.commit()
  
  print('start')
  print('Total {0} data saved'.format(len(data)))
  cursor.close()
  cnx.close()
    
  # except Exception as e:
  #   print('Error!', e)
  
  
  
  
def get_title_url_from_db():
  '''
  @description: 
  @param {*}
  @return {*}
  '''  
  
  title_list_from_db = []
  url_list_from_db = []
  try:
    cnx = SqlCon.connect(database='newsdb',
                        user='root')
    cursor = cnx.cursor(named_tuple=True)
    query = ''' select * from newsdb.news_details_tbl '''
    
    cursor.execute(query)
    res = cursor.fetchall()
    for entity in res:
      title_list_from_db.append(entity.news_title)
      url_list_from_db.append(entity.news_url)
    cursor.close()
    cnx.close()
    
  except Exception as e:
    print(e)
    
  return title_list_from_db, url_list_from_db
  
@timer
def main():
  # host = 'https://news.google.com/articles/CBMijAFodHRwczovL3d3dy5uemhlcmFsZC5jby5uei9uei9jb3ZpZC0xOS1jb3JvbmF2aXJ1cy10cmF2ZWwtYnViYmxlLXBhdXNlLXdpdGgtdmljdG9yaWEtZXh0ZW5kZWQtYS1mdXJ0aGVyLXR3by1kYXlzL0gzTDdLRVNCTkxZNkNIQkRUT1NIQ0JXU1dJL9IBAA?hl=en-NZ&amp;gl=NZ&amp;ceid=NZ%3Aen'
  
  host = 'https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR04wZDE5aUVnSmxiaWdBUAE?hl=en-NZ&gl=NZ&ceid=NZ%3Aen'

  # title_list_in_db, url_list_in_db = get_title_url_from_db()
  # entities = get_entity(host, title_list_in_db, url_list_in_db)
  entities = get_entity(host, [], [])
  # save_data_to_db(entities)


if __name__ == '__main__':
  main()