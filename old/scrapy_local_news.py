# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
import os
import re
import pyodbc
import time
# from googletrans import Translator



def get_urls(host):
  url_list_stuff = []
  url_list_herald = []
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
  """从google news new zealand页面获取文章URL"""
  response = requests.get(host, headers)  # 发起网络请求，获得响应
  soup = BeautifulSoup(response.text, 'html.parser') # 使用BeautifulSoup解析，查找想要的内容。html.parser是熊内置的解析方案，可以不填会有warning
  #在google new上找到整个body的div，在这个div下面找每篇文章的div，在每篇文章的div下面找发布源和文章的链接。
  for div_node in soup.findAll('div'):
    if (div_node.get('jscontroller')) == 'd0DtYd' or (div_node.get('jslog') == 93789):
      publisher = div_node.find('div', {'class': 'SVJrMe'}).find('a').text
      if publisher == 'Stuff.co.nz':
        href_node = div_node.find('h3').find('a')
        url_article = 'https://news.google.com' + href_node['href'].replace('.', '')
        response = requests.get(url_article, headers)
        if not 'quizzes' in response.url:
          url_list_stuff.append(url_article)
        # print(url_article)
      elif publisher == 'New Zealand Herald':
        href_node = div_node.find('h3').find('a')
        url_article = 'https://news.google.com' + href_node['href'].replace('.', '')
         # response.url是响应的地址，不一定是原始请求地址，因为网站可能会把对请求做重定向
        # url_article = urljoin(response.url, href)
        url_list_herald.append(url_article)
        # print(url_article)
      else:
        continue
  print('文章URL抓取完成')
  return {'stuff': url_list_stuff, 'herald': url_list_herald}



def get_info_stuff(url):
  """get title, publish date, content, image of the article """
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
  response = requests.get(url, headers)  # 发起网络请求，获得响应
  response.encoding = 'utf-8'  # 网页编码
  url = response.url
  #过滤掉带有quiz的url
  soup = BeautifulSoup(response.text, 'html.parser')  # 使用BeautifulSoup解析，查找想要的内容。html.parser是熊内置的解析方案，可以不填会有warning
  title = soup.find('h1').text.strip().replace("'","''")
  timestamp = soup.find('span', {'itemprop': 'dateModified'}).text
  source = 'Stuff'
  original_author = ''
  try:
    original_author = soup.find('span', {'itemprop': 'name'}).text.strip().replace("'","''")
  except Exception as ex:
    print("出现如下异常: %s" % ex)
    print(url + '文章没有作者信息')
  """正文包含视频链接"""
  content = soup.find('p', {'class': 'sics-component__html-injector sics-component__story__intro sics-component__story__paragraph'}).text.strip()
  for p_node in soup.find('span', {'class': 'sics-component__story__body sics-component__story__body--nativform'}).findAll('p', {'class': 'sics-component__html-injector sics-component__story__paragraph'}):
    content += '\n' + '\n' + p_node.text.strip()
    content = content.replace("'","''")
  get_img(soup.find('span', {'class': 'sics-component__story__body sics-component__story__body--nativform'}).findAll('meta', {'itemprop': 'url'}), url)
  print(url+' '+'抓取完成')
  return {'url': url, 'title': title, 'date_publish': timestamp, 'source': source, 'original_author': original_author, 'content': content}







def get_info_herald(url):
  """get title, publish date, content, image of the article """
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
  response = requests.get(url, headers)  # 发起网络请求，获得响应
  response.encoding = 'utf-8'  # 网页编码
  url = response.url
  soup = BeautifulSoup(response.text, 'html.parser')  # 使用BeautifulSoup解析，查找想要的内容。html.parser是熊内置的解析方案，可以不填会有warning
  title = soup.find('h1', {'class': 'article__heading'}).text.strip().replace("'","''")
  timestamp = soup.find('time', {'class': 'meta-data__time-stamp'}).text
  #时间格式满足 时刻在前日期在后
  timestamp = timestamp[-8:]+' '+timestamp[:-9]
  source = 'NZherald'
  original_author = ''
  try:
    original_author = soup.find('div', {'class': 'author__name'}).text.strip().replace("'","''")
  except Exception as ex:
    print("出现如下异常: %s" % ex)
    print(url + '文章没有作者信息')
  """正文包含视频链接"""
  content = ''
  for p_node in soup.find('section', {'class': 'article__body full-content article__content'}).findAll('p'):
    content += p_node.text.strip() + '\n' + '\n'
  content = content.strip().replace("'","''")
  imgs = []
  for figure_node in soup.find('section', {'class': 'article__body full-content article__content'}).findAll('figure', {'class': 'figure'}):
    imgs.append(figure_node.find('img'))
  get_img(imgs, url)
  print(url+' '+'抓取完成')
  return {'url': url, 'title': title, 'date_publish': timestamp, 'source': source, 'original_author': original_author, 'content': content}




def mkdir(path):
  """create directories to save images"""
  folder = os.path.exists(path)

  if not folder:
    os.makedirs(path)
    return True
  else:
    print('--- folder already exists ---')
    return False




def get_img(imgs, url):
  """创建文章的文件夹保存图片"""
  #local_path是抓取图片存储的根目录
  local_path = r"D:\Desktop\img_local_news"
  if imgs:
    img_src = ''
    folder_path = local_path + '\\' + url.split('/')[-2]
    if mkdir(folder_path):
      for index, img in enumerate(imgs):
        if img.get('content'):
          img_src = img.get('content').split('?')[0]
        else:
          img_src = img.get('data-srcset').strip().split(' ')[2]
          img_src = img_src.strip().replace('320w,', '')
        try:
          if img_src[-3:] == 'gif':
            img_name = folder_path+'\\'+str(index + 1)+'.gif'
            urllib.request.urlretrieve(img_src, img_name)
          elif img_src[-3:] == 'png':
            img_name = folder_path+'\\'+str(index + 1)+'.png'
            urllib.request.urlretrieve(img_src, img_name)
          elif img_src[-4:] == 'jpeg':
            img_name = folder_path+'\\'+str(index + 1)+'.jpeg'
            urllib.request.urlretrieve(img_src, img_name)
          else:
            img_name = folder_path+'\\'+str(index + 1)+'.jpg'
            urllib.request.urlretrieve(img_src, img_name)
          print("文件下载保存到本地成功")
          print("Img Src: "+ img_src)
          print("URL: "+ url)
        except Exception as ex:
          print("出现如下异常: %s" % ex)
          print("文件下载保存到本地出错")
          print("Img Src: "+ img_src)
          print("Directory: " + img_name)
          print("URL: "+ url)


# def get_img_herald(imgs, url):
# 	"""创建文章的文件夹保存图片"""
# 	if imgs:
# 		folder_path = local_path + '\\' + url.split('/')[-2]
# 		if mkdir(folder_path):
# 			for index, img in enumerate(imgs):
# 				img_src = img.get('content').split('?')[0]
# 				print(img_src)
# 				try:
# 					if img_src[-3:] == 'gif':
# 						img_name = folder_path+'\\'+str(index + 1)+'.gif'
# 						urllib.request.urlretrieve(img_src, img_name)
# 					elif img_src[-3:] == 'png':
# 						img_name = folder_path+'\\'+str(index + 1)+'.png'
# 						urllib.request.urlretrieve(img_src, img_name)
# 					elif img_src[-4:] == 'jpeg':
# 						img_name = folder_path+'\\'+str(index + 1)+'.jpeg'
# 						urllib.request.urlretrieve(img_src, img_name)
# 					else:
# 						img_name = folder_path+'\\'+str(index + 1)+'.jpg'
# 						urllib.request.urlretrieve(img_src, img_name)
# 				except Exception as ex:
# 					print("出现如下异常: %s" % ex)
# 					print("文件下载保存到本地出错")
# 					print("Img Src: "+ img_src)
# 					print("Directory: " + img_name)
# 					print("URL: "+ url)



def save_info_to_db(info_list):
  '''将获取到的文章信息存储到数据库'''
  #file_path是access文件的绝对路径
  file_path = r'D:\Download\Database1.accdb'
  conn = pyodbc.connect(u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+ file_path)
  cursor=conn.cursor()
  # # 创建表格
  # try:
  # 	cursor.execute("CREATE TABLE local_news_table(url Text, title Text, date_publish Text, source Text, original_author Text, content Memo, published Bit)")
  # 	conn.commit()
  # except:
  # 	print("出现如下异常: %s" % ex)
  # 	print("创建表格失败")
  # 	return False
  for info in info_list:
    url = info.get('url')
    title = info.get('title')
    date_publish = info.get('date_publish')
    source = info.get('source')
    original_author = info.get('original_author')
    content = info.get('content')
    #sql query if the title is already in the table
    result = cursor.execute("SELECT * FROM local_news_table WHERE url = '%s'" % url)
    data = result.fetchall()
    if not data:
      try:
        sql = "INSERT INTO local_news_table VALUES('%s', '%s', '%s', '%s', '%s', '%s', %d)" % (url, title, date_publish, source, original_author, content, 0)
        cursor.execute(sql)
        conn.commit()
        print('文章保存成功')
        print("Title: "+ title)
        print("URL: "+ url)
      except Exception as ex:
        print("出现如下异常: %s" % ex)
        print("文章保存失败")
        print("Title: "+ title)
        print("URL: "+ url)
    else:
      continue
  print('当前无新的文章录入')
  # try:
  # 	# 执行sql语句
  # 	提交到数据库执行
  # except:
  # 	# 如果发生错误则回滚
  # conn.rollback()
  # cur = cursor.execute('select * from myTable')
  # # 获取数据库中表的全部数据
  # data= cur.fetchall()
  # print(data)
  #关闭游标和链接
  cursor.close()
  conn.close()



# def save_translation_to_db():
#   '''将获取到的文章信息翻译成中文'''
#   #file_path是access文件的绝对路径
#   file_path = r'D:\Destktop\Spider\Database1.accdb'
#   conn = pyodbc.connect(u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+ file_path)
#   cursor = conn.cursor()
#   # # 创建表格
#   # try:
#   # 	cursor.execute("CREATE TABLE local_news_cn_table(url Text, title Text, date_publish Text, source Text, original_author Text, content Memo, published Bit)")
#   # 	conn.commit()
#   # except Exception as ex:
#   # 	print("出现如下异常: %s" % ex)
#   # 	print("创建表格失败")
#   # 	return False
#   #找出local_news表中所有没有被翻译的记录
#   result = cursor.execute("SELECT * FROM local_news_table WHERE translated = 0")
#   data = result.fetchall()
#   if data:
#     for row in data:
#       url = row[0]
#       title = row[1]
#       date_publish = row[2]
#       source = row[3]
#       original_author = row[4].replace("'", "''")
#       content = row[5]
#       try:
#         info = [title, content]
#         translated_info = trans(info)
#         title = translated_info[0].replace("'", "''")
#         content = translated_info[1].replace("'", "''")
#         try:
#           sql = "INSERT INTO local_news_cn_table VALUES('%s', '%s', '%s', '%s', '%s', '%s', %d)" % (url, title, date_publish, source, original_author, content, 0)
#           cursor.execute(sql)
#           conn.commit()
#           print('文章翻译成功并保存到local_news_cn_table')
#           print("Title: "+ title)
#           print("URL: "+ url)
#           # 翻译完文章 在local_news表中更新为已翻译
#           cursor.execute("UPDATE local_news_table SET translated = -1 WHERE url = '%s'" % url)
#           conn.commit()
#           print('文章在local_news_table中更新为已翻译')
#         except Exception as ex:
#           print("出现如下异常: %s" % ex)
#           print("文章翻译成功但保存到数据库失败")
#           print("Title: "+ title)
#           print("URL: "+ url)
#       except Exception as ex:
#         print("出现如下异常: %s" % ex)
#         print('文章翻译失败')
#         print("Title: "+ title)
#         print("URL: "+ url)
#   else:
#     print('当前所有文章均被翻译')
#   print('当前无新的文章录入')
#   # try:
#   # 	# 执行sql语句
#   # 	提交到数据库执行
#   # except:
#   # 	# 如果发生错误则回滚
#   # conn.rollback()
#   # cur = cursor.execute('select * from myTable')
#   # # 获取数据库中表的全部数据
#   # data= cur.fetchall()
#   # print(data)
#   #关闭游标和链接
#   cursor.close()
#   conn.close()


# def trans(info):
#   translated_info = []
#   translator = Translator()
#   translations = translator.translate(info, dest = 'zh-cn')
#   for translation in translations:
#     translated_info.append(translation.text)
#   return translated_info



def main():
  '''main function'''
  #host是google news的页面
  host = 'https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR04wZDE5aUVnSmxiaWdBUAE?hl=en-NZ&gl=NZ&ceid=NZ%3Aen'
  info_list = []
  for url in get_urls(host)['stuff']:
    if get_info_stuff(url):
      info_list.append(get_info_stuff(url))
  print('Stuff文章抓取完成')
  for url in get_urls(host)['herald']:
    info_list.append(get_info_herald(url))
  print('NZherald文章抓取完成')
  # save_info_to_db(info_list)
  # save_translation_to_db()
  print(info_list)


# save_translation_to_db()

if __name__ == '__main__':
  main()

# get_urls('https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNR04wZDE5aUVnSmxiaWdBUAE?hl=en-NZ&gl=NZ&ceid=NZ%3Aen')



# get_info_herald('https://news.google.com/articles/CBMijAFodHRwczovL3d3dy5uemhlcmFsZC5jby5uei9uei9wb2xpY2UtaHVudGluZy1mb3ItdGhpZXZlcy13aG8tc3RvbGUtMTAwMC13b3J0aC1vZi1vcm5hbWVudHMtZnJvbS1vYW1hcnUtZ2lmdC1zaG9wLzdURUdDUlhFT09MWEZKVDRJNktRWlBWVklJL9IBAA?hl=en-NZ&gl=NZ&ceid=NZ%3Aen')
