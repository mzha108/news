'''
Author       : Mu
Date         : 2021-08-26 10:57:06
LastEditors  : Mu
LastEditTime : 2021-08-26 15:21:06
Description  : 
'''

import requests
from lxml import html
import utils



def main(): 
  url = 'https://www.nzherald.co.nz/nz/covid-19-coronavirus-delta-outbreak-68-new-community-covid-cases-pm-jacinda-ardern-and-caroline-mcelnay/757RQKJFK53TMYYYWIQ34NKIQE/'
  headers = "header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}"
  response = requests.get(url, headers)
  
  if response.status_code >= 200 and response.status_code < 300:
    
    print("***** {0} *****".format(response.status_code))
    etree = html.etree
    html_obj = etree.HTML(response.text)
    
    post_time_xpath = '//*[@id="main"]/article/section[1]/header/div[1]/div/time/@datetime'
    tmp = html_obj.xpath(post_time_xpath)
    print(tmp)
  else:
    print("***** {0} *****".format(response.status_code))


if __name__ == '__main__': 
  main()