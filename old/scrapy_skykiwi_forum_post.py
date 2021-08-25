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


def connect_db_read_post(host, directory):
	#host是图片保存的根目录
	#链接数据库
	#db_path是access文件的绝对路径
	db_path = r'D:\Download\Database1.accdb'
	conn = pyodbc.connect(u'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+db_path)
	#创建游标
	cursor = conn.cursor()
	try:
		cur = cursor.execute("SELECT * FROM skykiwi_forum_room_rent WHERE published = 0")
		# 获取数据库中表的全部数据
		data = cur.fetchall()
		if data:
			d = open_Driver(host)
			for row in data:
				url = row[0]
				title = row[1]
				sub_title = row[2]
				post_message = row[3]
				try:
					post(d, host, directory ,url, title, sub_title, post_message)
					try:
						cursor.execute("UPDATE skykiwi_forum_room_rent SET published = -1 WHERE url = '%s'" % url)
						conn.commit()
						print(url + " 文章已经发表到网站且数据库已经更新发表状态")
					except Exception as ex:
						print("出现如下异常: %s" % ex)
						print(url + " 文章已经发表到网站但数据库更新发表状态失败")
				except Exception as ex:
					print("出现如下异常: %s" % ex)
					print(url + " 文章发表到网站失败")
		else:
			print("当前数据库表格中所有帖子均被发表")
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
	dlg['Open'].click()
	time.sleep(8)



def post(d, host, directory, url, title, sub_title, post_message):
	directory = directory + '\\' + url.split('=')[-2][:-6]
	cc = 1
	d.find_element_by_name('subject').send_keys(title)
	time.sleep(3)
	ActionChains(d).move_to_element_with_offset(d.find_element_by_xpath('//*[@id="e_iframe"]'), 1034, 363).click().send_keys(sub_title).send_keys(Keys.ENTER).send_keys(post_message).send_keys(Keys.ENTER).perform()
	time.sleep(3)

	if get_file_name(directory):
		d.find_element_by_xpath('//*[@id="e_image"]').click()
		time.sleep(3)
		for file_name in get_file_name(directory):
			if cc < 5:
				e = d.find_element_by_id('imgSpanButtonPlaceholder').click()
				time.sleep(5)
				windows_pop_up(file_name)
			else:
				break
			cc += 1
		if d.find_elements_by_xpath('//*[contains(@id, "image_td_")]'):
			for element in d.find_elements_by_xpath('//*[contains(@id, "image_td_")]'):
				element.find_element_by_tag_name('img').click()
				time.sleep(3)

	d.find_element_by_id('postsubmit').click()
	time.sleep(5)
	d.get(host)

# def validateTitle(title):
# 	"""替换字符串中不能用于文件名的字符"""
# 	rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
# 	new_title = re.sub(rstr, "_", title)  # 替换为下划线
# 	return new_title


def get_file_name(directory):
	file_name_list = []
	if os.path.exists(directory):
		files = os.listdir(directory)
		for file in files:
			file_name = directory + '\\' + file
			file_name_list.append(file_name)
	return file_name_list

def open_Driver(host):
	# chrome_options = Options()
	# chrome_options.add_experimental_option("detach", True)
	d = webdriver.Chrome()
	d.get(host)
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
	host = 'http://tangren.co.nz/forum.php?mod=post&action=newthread&fid=42'
	directory = r"D:\Desktop\img_skykiwi_forum\租房中心"
	connect_db_read_post(host, directory)


if __name__ == '__main__':
	main()
