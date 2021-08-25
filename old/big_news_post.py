# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pywinauto
from pywinauto.keyboard import send_keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import random
from selenium.webdriver.remote import switch_to
from selenium.webdriver.support.expected_conditions import frame_to_be_available_and_switch_to_it
from test.test_ssl import handle_error
import pyodbc


def login():
	# Login
	d.find_element_by_link_text('登陆').click()
	time.sleep(3)
	d.find_element_by_name('username').send_keys("tangren")
	# time.sleep(3)
	d.find_element_by_name('password').send_keys('jian1980_')
	# time.sleep(3)
	d.find_element_by_name('loginsubmit').click()


# # 随机验证码
# def yzm(len=6):
#     code_list = []
#     for i in range(10):  # 0-9数字
#         code_list.append(str(i))
#     for i in range(65, 91):  # 对应从“A”到“Z”的ASCII码
#         code_list.append(chr(i))
#     for i in range(97, 123):  # 对应从“a”到“z”的ASCII码
#         code_list.append(chr(i))
#         myslice = random.sample(code_list, len)  # 从list中随机获取6个元素，作为一个片断返回
#         verification_code = ''.join(myslice)  # list to string
#         return verification_code


def connect_db_read_post():
	#链接数据库
	#db_path是access文件的绝对路径
	db_path = r'D:\Download\Database1.accdb'
	conn = pyodbc.connect(u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+db_path)
	#创建游标
	cursor = conn.cursor()
	conn.commit()
	try:
		cur = cursor.execute("SELECT * FROM myTable WHERE published = No")
		# 获取数据库中表的全部数据
		data = cur.fetchall()
		if data:
			d = open_Driver()
			for row in data:
				url = row[0]
				title = row[1]
				date_publish = row[2]
				content = row[3]
				try:
					post(d, url, title, date_publish, content)
					try:
						cursor.execute("UPDATE myTable SET published = Yes WHERE url = '%s'" % url)
						conn.commit()
						print(url+" 文章已经发表到网站且数据库已经更新发表状态")
					except Exception as ex:
						print("出现如下异常: %s" % ex)
						print(url+" 文章已经发表到网站但数据库更新发表状态失败")
				except Exception as ex:
					print("出现如下异常: %s" % ex)
					print(url+" 文章发表到网站失败")
		else:
			print("当前数据库中所有文章均被发表")
	except Exception as ex:
		print("出现如下异常: %s" % ex)
		print("Error: ubale to fetch data")
	cursor.close()
	conn.close()



def windows_pop_up(file_name):
	#处理Windows窗口事件
	app = pywinauto.Desktop()
	dlg = app['Open']
	dlg['File name:Edit'].type_keys(file_name)
	time.sleep(3)
	dlg['Open'].click()
	time.sleep(10)



def post(d, url, title, date_publish, content):
	directory = r"D:\Desktop\img_news" + '\\' + url.split('=')[-1]
	c = 1
	cc = 1
	# d.get('http://tangren.co.nz/portal.php?mod=portalcp&ac=article&catid=5')
	# time.sleep(5)
	# d.maximize_window()

	d.find_element_by_name('title').send_keys(title)
	time.sleep(3)
	d.find_element_by_name('from').send_keys("留园网")
	time.sleep(3)
	d.find_element_by_name('fromurl').send_keys(url)
	time.sleep(3)
	d.find_element_by_name('dateline').send_keys(date_publish)
	time.sleep(3)

	ActionChains(d).move_to_element_with_offset(d.find_element_by_xpath('//*[@id="uchome-ifrHtmlEditor"]'), 379.25, 14).click().perform()
	time.sleep(5)

	for file_name in get_file_name(directory):
		if cc < 5:
			e = d.find_element_by_id('imgSpanButtonPlaceholder')
			time.sleep(3)
			ActionChains(d).move_to_element(d.find_element_by_id('imgSpanButtonPlaceholder')).click().perform()
			time.sleep(5)
			windows_pop_up(file_name)
		else:
			break
		cc += 1
	# ActionChains(d).move_by_offset(-x, -y).perform() #将鼠标位置恢复到移动前


	for element in d.find_elements_by_xpath('//*[contains(@id, "attach_list_")]'):
		if c == 1:
			element.find_element_by_tag_name('img').click()
			time.sleep(5)
			element.find_element_by_tag_name('input').click()
			time.sleep(5)
			ActionChains(d).move_to_element_with_offset(d.find_element_by_xpath('//*[@id="uchome-ifrHtmlEditor"]'), 1000, 350).click().send_keys(Keys.ENTER).send_keys(content).send_keys(Keys.ENTER).perform()
			time.sleep(5)
		else:
			element.find_element_by_tag_name('img').click()
			time.sleep(5)
		c += 1

	d.find_element_by_xpath('//*[@id="issuance"]/strong').click()
	time.sleep(8)
	d.find_element_by_link_text('继续发布新文章').click()
	time.sleep(8)


# def validateTitle(title):
# 	"""替换字符串中不能用于文件名的字符"""
# 	rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
# 	new_title = re.sub(rstr, "_", title)  # 替换为下划线
# 	return new_title


def get_file_name(directory):
	file_name_list = []
	files = os.listdir(directory)
	for file in files:
		file_name = directory + '\\' + file
		file_name_list.append(file_name)
		# print(file_name)
	return file_name_list

def open_Driver():
	# chrome_options = Options()
	# chrome_options.add_experimental_option("detach", True)
	d = webdriver.Chrome()
	d.get('http://tangren.co.nz/portal.php?mod=portalcp&ac=article&catid=5')
	d.maximize_window()
	time.sleep(5)
	d.find_element_by_xpath('//*[@id="toptb"]/div/div[2]/div/div/div/ul/li[1]/a').click()
	time.sleep(5)
	d.find_element_by_name('username').send_keys("admin")
	time.sleep(3)
	d.find_element_by_name('password').send_keys('jian1980_')
	time.sleep(3)
	d.find_element_by_name('loginsubmit').click()
	time.sleep(5)
	return d



def main():
	'''main function'''
	connect_db_read_post()



if __name__ == '__main__':
	main()




