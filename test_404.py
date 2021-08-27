'''
Author       : Mu
Date         : 2021-08-26 10:57:06
@LastEditors  : Mu
@LastEditTime : 2021-08-27 17:04:10
Description  : 
'''

import requests
from lxml import html
import utils



def main(): 
  # url = 'https://www.nzherald.co.nz/nz/afghanistan-fall-kabul-terror-threat-new-zealanders-told-stay-away-from-airport/WCPWK4EFXR4IF7D2ICEBHXMMC4/'
  # headers = "header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}"
  # response = requests.get(url, headers)
  
  # if response.status_code >= 200 and response.status_code < 300:
    
  #   print("***** {0} *****".format(response.status_code))
  #   etree = html.etree
  #   html_obj = etree.HTML(response.text)

  #   imgs_list = []
  #   imgs_figure_xpath =       '//*[@id="main"]/article/section[1]/section[2]//div[@class="article-media"]/figure{0}'
  #   imgs = html_obj.xpath(imgs_figure_xpath.format(''))
  #   for i in range(len(imgs)):
  #     imgs_title = imgs[i].xpath('figcaption/text()')
  #     img = str(imgs[i].xpath('img/@data-srcset')).split(',')[-1].split(' ')[0]
  #     if not imgs_title:
  #       imgs_list.append({'title': 'no-title', 'img': img})
  #     else:
  #       imgs_list.append({'title': imgs_title, 'img': img})
  # else:
  #   print("***** {0} *****".format(response.status_code))
  str = "Our priority for this mission was always a time-sensitive one;<EOP> to evacuate New Zealand citizens, permanent residents<EOP> and those at risk due to their association with New Zealand via the criteria set by Cabinet."
  
  new_str = str.split('<EOP>')
  print(len(new_str))
  for x in new_str:
    print(x.strip())
  


if __name__ == '__main__': 
  main()