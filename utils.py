'''
@Author       : Mu
@Date         : 2021-08-25 22:23:45
@LastEditors  : Mu
@LastEditTime : 2021-08-26 17:25:30
@Description  : 
'''


from datetime import date, datetime, timezone
import time
import math
import mysql.connector


def timer(func):
  '''
  @description: 
  @param {*} func
  @return {*}
  '''
  def wrapper(*args, **kw):
    a = time.time()
    res = func(*args)
    b = time.time()
  
    print("Total time used: {:.4} s".format(b - a))
    return res
  return wrapper


def time_diff(time_str:str):
  '''
  @description: 
  @param {str} time_str
  @return {*}
  '''
  time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
  now = datetime.utcnow()

  diff_in_sec = (now - time).total_seconds()

  return math.floor(diff_in_sec / 3600)


def save_to_db(entities):
  '''
  @description: 
  @param {*} entities
  @return {*}
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