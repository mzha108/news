'''
Author       : Mu
Date         : 2021-07-31 17:07:07
LastEditTime : 2021-08-25 22:31:36
LastEditors  : Mu
Description  : 
'''

from typing import Tuple
import requests
from lxml import html
from fake_useragent import UserAgent
from utils import time_diff, timer, save_to_db

# entity = {
#         'news_title': str(news_title),
#         'news_publisher': str(publisher),
#         'post_date': str(post_date),
#         'news_url': str(news_url),
#         'img_url': article_imgs,
#         'news_content': str(news_content)
#       }


def get_entity(html_obj, headers):
  '''
  description: 
  param {*} html_obj
  param {*} headers
  return {*}
  '''
  
  root_xpath = '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div/div[2]/div/main/c-wiz/div/div/main/div[1]/div' # news block 
  news_list = html_obj.xpath(root_xpath)
  print("========== Total number of news: ", len(news_list), "==========")
  if len(news_list) > 0:
    # check if there are at least one news
    count_no_sub_list = 0
    count_sub_list = 0
    # get all news 
    for index, item in enumerate(news_list):
      if len(item.xpath('div/div')) == 0:
        # news has no sub list
        
        print("news: ",index+1)
        print('only one news')
        count_no_sub_list += 1
        pass
      else:
        # news has sub list
        
        print("news: ", index+1)
        print('more than one news')
        
        count_sub_list += 1
        news_publisher, news_published_time = get_news_publisher_and_time(item, True)
        print(news_publisher, '****************')
        if is_nzh_or_stuff(news_publisher):
          # nzh or stuff
          print("nzh or stuff found in main area.")
          news_title = get_news_title(item)
          news_url = get_url('main_title')(item, headers)
          news_post_date = get_post_date_from_origin(news_url, headers)
          # news_content = get_news_content()
          # news_img_url = get_news_img_url()

        else:
          # not nzh or stuff
          print('not found in main area. Finding in sublist...')
          
          sub_list = get_news_sublist(item)
          for sub_item in sub_list:
            news_publisher, news_published_time = get_news_publisher_and_time_in_sublist(sub_item)
            print('&&&&&&&&&&&&&', news_publisher, ' ', is_nzh_or_stuff(news_publisher), ' ', is_old(news_published_time))
            if is_nzh_or_stuff(news_publisher) and not is_old(news_published_time):
              # publisher in sub list is nzh or stuff
              print('found nzh or stuff. in sublist', news_publisher)
              news_title = get_news_title_from_sublist(sub_item)
              # news_google_url = get_google_url_from_sublist(sub_item)
              break
            else:
              # publisher in sub list is not nzh or stuff
              print('no nzh or stuff found for this news...')
            
        pass
    print('count_no_sub_list', count_no_sub_list, '  ', 'count_sub_list', count_sub_list)
    
  else:
    # no news found
    print("No news found! Please check root xpath.")


def get_post_date_from_origin(news_url:str, headers:str):
  try:
    response = requests.get(news_url, headers)
  except Exception as e:
    print(e)

  if response.status_code >= 200 and response.status_code < 300:
    print("test")
    pass


  pass



def get_news_title(item:html) -> list:
  '''
  description: 
  param {html} item
  return {*}
  '''
  news_title_path = 'div/div/article/h3/a/text()'
  news_title = item.xpath(news_title_path)
  print('news title from main: ', news_title)
  return news_title

def get_news_title_from_sublist(item:html) -> list:
  '''
  description: 
  param {html} item
  return {*}
  '''
  # get news title
  news_title_path = 'h4/a/text()'
  news_title = item.xpath(news_title_path)
  print('news title from sublist: ', news_title)
  return news_title
  
def get_url(flag:str):
  '''
  description: 
  param {str} flag
  return {*}
  '''
  def get_google_url_from_main_title(item:html, headers:str) -> list:
    # get google url from main title
    # root: '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div/div[2]/div/main/c-wiz/div/div/main/div[1]/div'
    if flag == 'main_title':
      google_url_path = 'div/div/article/h3/a/@href'
    if flag == 'from_sublist':
      google_url_path = '../a/@href'
    if flag == 'no_sub':
      google_url_path = '../a/@href'
      
    google_url = item.xpath(google_url_path)
    print('@href: ', google_url)
    url = get_news_url(google_url, headers)
    print("news url: ", url)
    return url
  return get_google_url_from_main_title


def get_news_url(google_url:str, headers:str) -> str:
  '''
  description: 
  param {str} google_url
  param {str} headers
  return {*}
  '''
  url = 'https://news.google.com/' + google_url[0].replace('./', '')
  response = requests.get(url, headers)
  return response.url


def get_news_sublist(item:html) -> list:
  '''
  description: 
  param {html} item
  return {*}
  '''
  sub_list_path = 'div/div/div[1]/article'
  sub_list = item.xpath(sub_list_path)
  return sub_list
  
def get_news_publisher_and_time(item:html, flag:bool) -> Tuple[list, list]:
  '''
  description: 
  param {html} item
  param {bool} flag
  return {*}
  '''
  news_publisher_path = 'div/div/article/div/div/a/text()'
  news_published_time_path = 'div/div/article/div/div/time/@datetime'
  
  news_publisher = item.xpath(news_publisher_path)
  news_published_time = item.xpath(news_published_time_path)
  
  return (news_publisher, news_published_time)

def get_news_publisher_and_time_in_sublist(item:html) -> Tuple[list, list]:
  '''
  description: 
  param {html} item
  return {*}
  '''
  news_publisher_path = 'div/div/a/text()'
  news_published_time_path = 'div/div/time/@datetime'
  
  news_publisher = item.xpath(news_publisher_path)
  news_published_time = item.xpath(news_published_time_path)
  return (news_publisher, news_published_time)
  

def is_nzh_or_stuff(news_publisher:list) -> bool:
  '''
  description: 
  param {list} news_publisher
  return {*}
  '''
  if news_publisher[0] == 'New Zealand Herald' or news_publisher[0] == 'Stuff.co.nz' :
    return True
  else:
    return False
  

def is_old(news_published_utc_time):
  '''
  description: 
  param {*} news_published_utc_time
  return {*}
  '''
  time = time_diff(news_published_utc_time[0])
  if time <= 24:
    print("young")
    return False 
  else:
    print("Too old > 24 hours")
    return True
  


@timer
def main():
  # ua = UserAgent(verify_ssl=False)
  # headers = ua.random
  headers = "header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}"
  url = 'https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR04wZDE5aUVnSmxiaWdBUAE?hl=en-NZ&gl=NZ&ceid=NZ%3Aen'
  try:
    response = requests.get(url, headers)
  except Exception as e:
    print(e)

  if response.status_code >= 200 and response.status_code < 300:
    etree = html.etree
    html_obj = etree.HTML(response.text)

    try:
      get_entity(html_obj, headers)
    except Exception as e:
      print(e)
  else:
    print("Error. Response status code == {0}".format(response.status_code))

if __name__ == '__main__':
  main()

