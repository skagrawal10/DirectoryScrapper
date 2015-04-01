import smtplib
from scrapy.exceptions import CloseSpider
from scrapy.spider import BaseSpider
from scrapy.http import FormRequest,Request,Response,HtmlResponse,XmlResponse
from scrapy.selector import HtmlXPathSelector
from scrapy.item import Item, Field
import os
import re
import time
import datetime
import csv
import traceback
import urllib2
import signal
import math
import sys
from middlewares import *

class yellowpagesSpider(BaseSpider):
	
	name='yelp'
	start_urls = ['http://www.yelp.com/search?find_desc=Coffee+%26+Tea&find_loc=Los+Angeles']
	download_delay = 2
	
	def __init__(self, name=None, **kwargs): 
		self.projectName='yelp'
		self.baseURL = 'http://www.yelp.com/'
		log=[]
		
		MAX_download_delay = 10
		print 'Yelp Spider Started!!!'
		file_name = kwargs['file_name']
		file = open(file_name, 'ab')
		self.writer = csv.writer(file)
		self.writer.writerow(['Source_URL','Name','Phone_Number','Street','City','State','Website'])
		
		
	def parse(self, response):
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'GetList: '+response.url
			
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 			
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		next_page_link = "http://www.yelp.com" + hxs.select('.//a[@class="page-option available-number"]//@href').extract()[0].strip()
		req = Request(url=next_page_link, priority=2, callback=self.parse)
		reqs = [];
		reqs.append(req);
		items = hxs.select('//div[contains(@class,"search-result")]')
		for item in items:
			name = ""
			phone_no=""
			street_addr=""
			locality=""
			region=""
			postal=""
			website=""
			url = ""
			try:
				url = self.baseURL + item.select('.//a[@class="biz-name"]//@href').extract()[0].strip()
				try:
					name = item.select('.//a[@class="biz-name"]//text()').extract()[0].strip()
				except:
					pass;
				try:
					street_addr = item.select('.//address//text()').extract()[0].strip()
				except:
					pass;
				try:
					locality = item.select('.//span[@class="neighborhood-str-list"]//text()').extract()[0].strip(',').strip()
				except:
					pass;
				try:
					phone_no = item.select('.//span[@class="biz-phone"]//text()').extract()[0].strip()
				except:
					pass;
				
			except:
				pass
				
			info = [url,name,phone_no,street_addr,locality,website]
			self.writer.writerow(info)
		return;
		#return reqs;	
		

	def handler(self, signum, frame):
		print "Parsing function taking forever!!"
		raise Exception("end of time")
	
	def error(self, response):
		#self.logger.write('Error on url: ', response.url)
		print 'ERROR: '+response.url
		print 'ERROR code: '+str(response.status)
		#print 'ERROR proxy: '+str(response.proxy)
		
	def removeTags(self, element):
		try:
			element = str(element.encode('ascii','ignore'))
		except UnicodeError:
			element = str(element)
		except:
			element = str(element).encode('ascii','ignore')
		t=''
		s=element
		while s.find('<')>-1:
			i=0
			j=s.find('<')
			t+=s[i:j]
			i=s.find('>')+1
			s=s[i:]
			t+=' '
		t+=s
		return t.strip()

