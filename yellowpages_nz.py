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
	
	name='yellowpages_nz'
	start_urls = ['http://yellow.co.nz/new-zealand/cafes/?what=Cafes&where=new-zealand']

	download_delay = 2
	
	def __init__(self, name=None, **kwargs): 
		self.projectName='yellowpages'
		self.baseURL = 'http://www.yellowpages.com/'
		log=[]
	
		MAX_download_delay = 10
		print 'Yellowpages Spider Started!!!'

		file_name = kwargs['file_name']
		file = open(file_name, 'ab')
		self.writer = csv.writer(file)
		
		
		self.writer.writerow(['Source_URL','Name','Phone_Number','Street','City','State','Website', 'Email'])
		
		
	def parse(self, response):
		self.baseURL = response.url;
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'Getdetails: '+response.url#, 'PROXY: '+str(response.meta['proxy'])
		
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		reqs = []
		page_no=1
		page_string = hxs.select('//div[@id="searchResultsNumber"]/text()')[0].extract().strip();
		print "Page String - " + page_string;
		no_pages = 1;
		try:
			no_pages = int(math.ceil(int(page_string.split("of")[1].replace("Results", "").strip())/20.0));
		except:
			pass;
		print "No of pages - " + str(no_pages);
		while page_no<=no_pages:			
			parts = response.url.split("?");
			url = parts[0] + "/page/" + str(page_no) + "?" + parts[1];
			req = Request(url=url, priority=2, callback=self.getList)
			reqs.append(req)
			page_no += 1
			#if page_no>2:
			#	break;
		return reqs

		
	def getList(self, response):
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'GetList: '+response.url
			
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 			
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		
		list1 = hxs.select('//div[contains(@class,"resultsListItem")]')
		
		for card in list1:
			url = ''
			name = ''
			address = ''
			suburb = ''
			latitude = ''
			longitude = ''
			phone = ''
			email = ''
			website = ''
			category2 = ''
			
			try:
				url = "www.yellowpages.com.nz" + card.select('.//a[@data-ga-id="Business_Name_Link"]/@href').extract()[0].strip()
				print url;
			except:
				pass
			try:
				name = card.select('.//a[@data-ga-id="Business_Name_Link"]/@title').extract()[0].strip()
			except:
				pass
			try:
				address = card.select('.//a[@data-ga-id="Address_Link"]/text()').extract()[0].strip()
			except:
				pass
			try:
				phone = card.select('.//meta[@itemprop="telephone"]/@content').extract()[0].strip();
			except:
				pass
			try:
				website = card.select('.//a[@data-ga-id="Website_Link"]/@href').extract()[0].strip()
			except:
				pass
			try:
				email = card.select('.//a[@data-ga-id="Email_Link"]/@href').extract()[0].strip().split(":")[1].strip();
			except:
				pass
			self.writer.writerow([url, name, phone, address, "", "", website, email])
			
		return
		
	
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

