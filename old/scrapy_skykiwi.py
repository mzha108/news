# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
import os
import re
import pyodbc
import time




#file_path是access文件的绝对路径
file_path = r'D:\Download\Database1.accdb'
#host是新闻速递首页的url
host = 'http://news.skykiwi.com/na/index.shtml'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
#local_path是抓取图片存储的根目录
local_path = r"D:\Desktop\img_skykiwi_news"




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
	div_node = soup.find('div', {'id': 'main_left'})  # 查找id值为d_list的div标签，
	for li_node in div_node.findAll('li'):  # 使用find_all()找出所有<li>标签，在for循环中解析每个<li>标签
		href = li_node.find('a')['href']  # 打印出li标签链接（href属性的值）
		if 'news' in href:
			url_article = urljoin(response.url, href) # response.url是响应的地址，不一定是原始请求地址哦，因为网站可能会把对请求做重定向
			url_list.append(url_article)
	return url_list

def test():
	url_list = []
	"""从新闻速递首页获取文章URL"""
	try:
		response = requests.get('http://news.skykiwi.com/', headers)  # 发起网络请求，获得响应
		soup = BeautifulSoup(response.text, 'html.parser') # 使用BeautifulSoup解析，查找想要的内容。html.parser是熊内置的解析方案，可以不填会有warning
		div_node = soup.find('div', {'id': 'center-main'})  # 查找id值为d_list的div标签，
		ul_node = div_node.find('ul', {'id': 'ul-news-nalist'})  # 在div标签下查找第一个ul标签
		for li_node in ul_node.findAll('li'):  # 使用find_all()找出所有<li>标签，在for循环中解析每个<li>标签
			href = li_node.find('a')['href']  # 打印出li标签链接（href属性的值）
			url_article = urljoin(response.url, href) # response.url是响应的地址，不一定是原始请求地址哦，因为网站可能会把对请求做重定向
			url_list.append(url_article)
			print(href)
	except Exception as ex:
		print("出现如下异常: %s" % ex)
	return url_list



def get_info(url):
	"""get title, publish date, content, image of the article """
	response = requests.get(url, headers)  # 发起网络请求，获得响应
	response.encoding = 'utf-8'  # 网页编码
	str_contents = ''
	soup = BeautifulSoup(response.text, 'html.parser')  # 使用BeautifulSoup解析，查找想要的内容。html.parser是熊内置的解析方案，可以不填会有warning
	title = soup.find('h1').text.strip()
	sub_title = soup.find('h5').text.strip().replace('\r', '').replace('\n', '').replace('\t', '')
	timestamp = "".join(re.findall(".*期(.*)阅.*", sub_title)).strip()[1:]
	"""正文包含视频链接"""
	body = get_vid_link(soup.find('div', {'class': 'artText'}).findAll('iframe')) + soup.find('div', {'class': 'artText'}).text.strip().replace("'","''")
	# for content in soup.find('div', {'id': 'ea_content'}).children:
	# 	print(content)
	"""返回所有子节点的列表"""
	contents = soup.find('div', {'class': 'artText'}).contents
	"""遍历列表，把所有子节点的内容存储在一个字符串中"""
	for node in contents:
		str_contents += str(node).strip().replace("'","''")
	get_img(soup.find('div', {'class': 'artText'}).findAll('img'), title, url)
	return {'url': url, 'title': title, 'date_publish': timestamp, 'body': body, 'contents': str_contents}



def get_img(imgs, title_article, url):
	"""创建文章的文件夹保存图片"""
	if imgs:
		img_name = ''
		# new_title_article = validateTitle(title_article)
		folder_path = local_path + '\\' + url.split('/')[-1].split('.')[0]
		if mkdir(folder_path):
			for index, img in enumerate(imgs):
				img_src = img.get('src')
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
				except Exception as ex:
					print("出现如下异常: %s" % ex)
					print("文件下载保存到本地出错")
					print("Img Src: "+ img_src)
					print("Directory: " + img_name)
					print("URL: "+ url)



def get_vid_link(vid_links):
	video_links = ''
	if vid_links:
		for video in vid_links:
			video_src = video.get('src')
			video_links += video_src + '[v]'
	return video_links


# def validateTitle(title):
# 	"""替换字符串中不能用于文件名的字符"""
# 	rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
# 	new_title = re.sub(rstr, "_", title)  # 替换为下划线
# 	return new_title



def save_info_to_db(info_list):
	'''将获取到的文章信息存储到数据库'''
	conn = pyodbc.connect(u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+file_path)
	cursor=conn.cursor()
	#创建表格
	# try:
	# 	cursor.execute("CREATE TABLE skykiwi_table(url Text, title Text, date_publish Text, body Memo, contents Memo)")
	# 	conn.commit()
	# except:
	# 	print("出现如下异常: %s" % ex)
	# 	print("创建表格失败")
	# 	return False
	for info in info_list:
		url = info.get('url')
		title = info.get('title')
		date_publish = info.get('date_publish')
		body = info.get('body')
		contents = info.get('contents')
		#sql query if the title is already in the table
		result = cursor.execute("SELECT * FROM skykiwi_table WHERE url = '%s'" % url)
		data = result.fetchall()
		try:
			if not data:
				sql = "INSERT INTO skykiwi_table VALUES('%s', '%s', '%s', '%s', '%s')" % (url, title, date_publish, body, contents)
				cursor.execute(sql)
				conn.commit()
		except Exception as ex:
			print("出现如下异常: %s" % ex)
			print("数据保存失败")
			print("Title: "+ title)
			print("URL: "+ url)
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



def main():
	'''main function'''
	info_list = []
	for url in get_urls(host):
		info_list.append(get_info(url))
		time.sleep(10)
	save_info_to_db(info_list)
	# info_list.clear()



if __name__ == '__main__':
	main()

# get_info('http://news.skykiwi.com/na/zh/2021-01-15/430839.shtml')
# cc = 'http://news.skykiwi.com/na/sh/2018-04-24/256991.shtml'
# c = cc.split('/')[-1].split('.')[0]




# def main():
# 	'''main function'''
# 	info_list = []
# 	info_list.append(get_info('https://www.6parknews.com/newspark/view.php?app=news&act=view&nid=461013'))
# 	save_info_to_db(info_list)




# ss = "https://www.6parknews.com/newspark/view.php?app=news&act=view&nid=461055"
# s = ss.split('=')
# print(s)
# print(s[-1])

# def st():
# 	for page in range(50):
# 		page+=1
# 		host= 'https://www.6parknews.com/newspark/index.php?p=%d' % (page)
# 		print(host)
# st()

# def test():
# 	'''将获取到的文章信息存储到数据库'''
# 	conn = pyodbc.connect(u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+file_path)
# 	cursor=conn.cursor()
# 	#创建表格
# 	info_list = [{'url': 'sss', 'title':'sss', 'date_publish':'sss','content':'sss'}]
# 	cursor.execute("CREATE TABLE myTable(url Text, title Text, date_publish Text, content Memo)")
# 	for info in info_list:
# 		#sql query if the title is already in the table
# 		result = cursor.execute("SELECT * FROM myTable WHERE url = '%s'" % (info.get('url')))
# 		data = result.fetchall()
# 		if not data:
# 			sql = "INSERT INTO myTable VALUES('%s', '%s', '%s', '%s')" % (info.get('url'), info.get('title'), info.get('date_publish'), info.get('content'))
# 			cursor.execute(sql)
# 	conn.commit()
# 	cursor.close()
# 	conn.close()
# test()



# dic = get_info('https://www.6parknews.com/newspark/view.php?app=news&act=view&nid=460994')



# string = 'jisong。。。'.replace('。。。','')
# print(string)


# t = 'jisong'
# path = 'D:\\Desktop\\img_news\\'+t
# # os.makedirs(path)
# img_src = 'https://web.popo8.com/202101/06/10/fad69fb394.jpg'
# urllib.request.urlretrieve(img_src, path+'\\%s.jpg')



#"D:\Desktop\img_news"
