# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
import os
import re
import pyodbc
import time



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
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
	"""从租房中心页面获取文章URL"""
	response = requests.get(host, headers)  # 发起网络请求，获得响应
	soup = BeautifulSoup(response.text, 'html.parser') # 使用BeautifulSoup解析，查找想要的内容。html.parser是熊内置的解析方案，可以不填会有warning
	if host.split('=')[-1] == '19':
		table_node = soup.find('table', {'summary': 'forum_19'})  # 查找id值为d_list的div标签，
		for tbody_node in table_node.findAll('tbody'):  # 使用find_all()找出所有<li>标签，在for循环中解析每个<li>标签
			if tbody_node.has_attr('id'):
				if 'normalthread' in tbody_node['id']:
					href = tbody_node.find('th').findAll('a')[2]['href']
					url_article = urljoin(response.url, href) # response.url是响应的地址，不一定是原始请求地址哦，因为网站可能会把对请求做重定向
					url_list.append(url_article)
				# print(url_article)
	elif host.split('=')[-1] == '17':
		table_node = soup.find('table', {'summary': 'forum_17'})  # 查找id值为d_list的div标签，
		for tbody_node in table_node.findAll('tbody'):  # 使用find_all()找出所有<li>标签，在for循环中解析每个<li>标签
			if tbody_node.has_attr('id'):
				if 'normalthread' in tbody_node['id']:
					href = tbody_node.find('th').findAll('a')[1]['href']
					url_article = urljoin(response.url, href) # response.url是响应的地址，不一定是原始请求地址哦，因为网站可能会把对请求做重定向
					url_list.append(url_article)
				# print(url_article)
	elif host.split('=')[-1] == '205':
		table_node = soup.find('table', {'summary': 'forum_205'})  # 查找id值为d_list的div标签，
		for tbody_node in table_node.findAll('tbody'):  # 使用find_all()找出所有<li>标签，在for循环中解析每个<li>标签
			if tbody_node.has_attr('id'):
				if 'normalthread' in tbody_node['id']:
					href = tbody_node.find('th').findAll('a')[1]['href']
					url_article = urljoin(response.url, href) # response.url是响应的地址，不一定是原始请求地址哦，因为网站可能会把对请求做重定向
					url_list.append(url_article)
				# print(url_article)
	else:
		table_node = soup.find('table', {'summary': 'forum_55'})  # 查找id值为d_list的div标签，
		for tbody_node in table_node.findAll('tbody'):  # 使用find_all()找出所有<li>标签，在for循环中解析每个<li>标签
			if tbody_node.has_attr('id'):
				if 'normalthread' in tbody_node['id']:
					href = tbody_node.find('th').findAll('a')[2]['href']
					url_article = urljoin(response.url, href) # response.url是响应的地址，不一定是原始请求地址哦，因为网站可能会把对请求做重定向
					url_list.append(url_article)
					# print(url_article)
	print(url_list)
	return url_list



def get_info(host, url):
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
	local_path = r"D:\Desktop\img_skykiwi_forum"
	sub_title = ''
	response = requests.get(url, headers)  # 发起网络请求，获得响应
	response.encoding = 'utf-8'  # 网页编码
	soup = BeautifulSoup(response.text, 'html.parser')
	title = soup.find('h1').findAll('a')[0].text.strip().replace("'","''") + soup.find('h1').findAll('a')[1].text.strip().replace("'","''")
	if host.split('=')[-1] == '19':
		local_path += '\\' + '租房中心'
		sub_title = soup.find('div', {'class': 'table-container'}).text.strip()
	elif host.split('=')[-1] == '17':
		local_path += '\\' + '二手市场'
		sub_title = soup.find('div', {'class': 'table-container'}).text.strip()
	elif host.split('=')[-1] == '205':
		local_path += '\\' + '大众服务'
		sub_title = soup.find('div', {'class': 'table-container'}).text.strip()
	else:
		local_path += '\\' + '求职招聘'
		sub_title = soup.find('div', {'class': 'table-container'}).text.strip()
	post_message = soup.find('td', {'class':'t_f'}).text
	if soup.find('td', {'class':'t_f'}).findAll('i'):
		i_node = soup.find('td', {'class':'t_f'}).find('i').text
		post_message = post_message.split(i_node)[0] + post_message.split(i_node)[1]
	for font_node in soup.find('td', {'class':'t_f'}).findAll('font'):
		if font_node.has_attr('class'):
			if font_node['class'][0] == 'jammer':
				post_message = post_message.split(font_node.text)[0] + post_message.split(font_node.text)[1]
	for span_node in soup.find('td', {'class':'t_f'}).findAll('span'):
		if span_node.has_attr('style'):
			if span_node['style'] == 'display:none':
				post_message = post_message.split(span_node.text)[0] + post_message.split(span_node.text)[1]
	for font_node in soup.find('td', {'class':'t_f'}).findAll('font'):
		if font_node.has_attr('style'):
			if font_node['style'] == 'font-size:7pt':
				post_message = post_message.split(font_node.text)[0] + post_message.split(font_node.text)[1]
	post_message = post_message.strip().replace('\r', '').replace('\n', '').replace('\t', '').replace("'","''")
	# print(title+sub_title+post_message)
	get_img(soup.find('td', {'class': 't_f'}).findAll('img'), url, local_path)
	return {'url': url, 'title': title, 'sub_title': sub_title, 'post_message': post_message}


def get_img(imgs, url, local_path):
	#local_path是抓取图片存储的根目录
	"""创建文章的文件夹保存图片"""
	folder_path = local_path + '\\' + url.split('=')[-2][:-6]
	if imgs:
		for img in imgs:
			if ('bbs.skykiwi.com' in img.get('src')) and ((img.get('src')[-3:] == 'gif') or (img.get('src')[-3:] == 'png') or (img.get('src')[-4:] == 'jpeg') or (img.get('src')[-3:] == 'jpg')):
				if mkdir(folder_path):
					for index, img in enumerate(imgs):
						img_src = img.get('src')
						try:
							if (img_src[-3:] == 'gif') and ('bbs.skykiwi.com' in img_src):
								img_name = folder_path+'\\'+str(index + 1)+'.gif'
								urllib.request.urlretrieve(img_src, img_name)
							elif (img_src[-3:] == 'png') and ('bbs.skykiwi.com' in img_src):
								img_name = folder_path+'\\'+str(index + 1)+'.png'
								urllib.request.urlretrieve(img_src, img_name)
							elif (img_src[-4:] == 'jpeg') and ('bbs.skykiwi.com' in img_src):
								img_name = folder_path+'\\'+str(index + 1)+'.jpeg'
								urllib.request.urlretrieve(img_src, img_name)
							elif (img_src[-3:] == 'jpg') and ('bbs.skykiwi.com' in img_src):
								img_name = folder_path+'\\'+str(index + 1)+'.jpg'
								urllib.request.urlretrieve(img_src, img_name)
							else:
								continue
						except Exception as ex:
							print("出现如下异常: %s" % ex)
							print("文件下载保存到本地出错")
							print("Img Src: "+ img_src)
							print("Directory: " + img_name)
							print("URL: "+ url)
					break


def get_vid_link(vid_links):
	video_links = ''
	if vid_links:
		for video in vid_links:
			video_src = video.get('src')
			video_links += video_src + '[v]'
	return video_links


def save_info_to_db(info_list):
	'''将获取到的文章信息存储到数据库'''
	#file_path是access文件的绝对路径
	file_path = r'D:\Download\Database1.accdb'
	conn = pyodbc.connect(u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+file_path)
	cursor=conn.cursor()
	# 创建表格
	# try:
	# 	cursor.execute("CREATE TABLE skykiwi_forum_job_recruitment(url Text, title Text, sub_title Text, post_message Memo, published Bit)")
	# 	conn.commit()
	# except Exception as ex:
	# 	print("出现如下异常: %s" % ex)
	# 	print("创建表格失败")
	# 	return False
	for info in info_list:
		url = info.get('url')
		title = info.get('title')
		sub_title = info.get('sub_title')
		post_message = info.get('post_message')
		#sql query if the title is already in the table
		result = cursor.execute("SELECT * FROM skykiwi_forum_job_recruitment WHERE url = '%s'" % url)
		data = result.fetchall()
		try:
			if not data:
				sql = "INSERT INTO skykiwi_forum_job_recruitment VALUES('%s', '%s', '%s', '%s', %d)" % (url, title, sub_title, post_message, 0)
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
	host = 'http://bbs.skykiwi.com/forum.php?mod=forumdisplay&fid=55'
	for url in get_urls(host):
		info_list.append(get_info(host, url))
	save_info_to_db(info_list)
	# info_list.clear()



if __name__ == '__main__':
	main()




