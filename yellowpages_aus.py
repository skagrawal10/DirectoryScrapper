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
	
	name='yellowpages_aus'
	start_urls = ['http://www.yellowpages.com.au/search/listings?clue=restaurants&locationClue=australia&lat=&lon=&referredBy=UNKNOWN&selectedViewMode=list&eventType=refinement&refinedCategory=42730']

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
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'Getdetails: '+response.url#, 'PROXY: '+str(response.meta['proxy'])
		
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		reqs = []
		req = Request(url=response.url, priority=2, callback=self.getList)
		reqs.append(req);
		page_no=1
		page_links = hxs.select('//div[@class="button-pagination-container"]/a/@href').extract()
		for link in page_links[:-1]:
			url = 'https://www.yellowpages.com.au' + link
			req = Request(url=url, priority=2, callback=self.getList)
			reqs.append(req);
			#break;
		return reqs

		
	def getList(self, response):
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'GetList: '+response.url
			
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 			
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		
		list1 = hxs.select('//div[contains(@class,"listing-search")]')
		
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
				url = 'https://www.yellowpages.com.au' + card.select('.//a[@class="listing-name"]/@href').extract()[0].strip()
				print url;
			except:
				pass
			try:
				name = card.select('.//a[@class="listing-name"]/text()').extract()[0].strip()
			except:
				pass
			try:
				category2 = ''.join(card.select('.//p[@class="listing-heading"]//text()').extract()).strip().split(' - ')[0]
			except:
				pass
			try:
				address = card.select('.//p[contains(@class,"listing-address")]/text()').extract()[0].strip()
			except:
				pass
			try:
				suburb = card.select('.//p[contains(@class,"listing-address")]/@data-address-suburb').extract()[0].strip()
			except:
				pass
			try:
				state = 'NSW'
			except:
				pass
			try:
				latitude = card.select('.//p[contains(@class,"listing-address")]/@data-geo-latitude').extract()[0].strip()
			except:
				pass
			try:
				longitude = card.select('.//p[contains(@class,"listing-address")]/@data-geo-longitude').extract()[0].strip()
			except:
				pass
			try:
				phone = card.select('.//a[contains(@class,"contact-phone")]//span[@class="contact-text"]/text()').extract()[0].strip()
			except:
				pass
			try:
				website = card.select('.//a[contains(@class,"contact-url")]/@href').extract()[0].strip()
			except:
				pass
			try:
				email = card.select('.//a[contains(@class,"contact-email")]/@data-email').extract()[0].strip()
			except:
				pass
			self.writer.writerow([url, name, phone, address, suburb, "", website, email])
			
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

