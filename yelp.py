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
import cStringIO
import codecs


class UnicodeWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""
	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()		

	def writerow(self, row):
		try:
			self.writer.writerow([unicode(s).encode("utf-8") for s in row])
			# Fetch UTF-8 output from the queue ...
			data = self.queue.getvalue()
			data = data.decode("utf-8")
			# ... and reencode it into the target encoding
			data = self.encoder.encode(data)
			# write to the target stream
			self.stream.write(data)
			# empty queue
			self.queue.truncate(0)
		except:
			pass

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)


class yellowpagesSpider(BaseSpider):
	
	name='yelp'
	#start_urls = ['http://www.yelp.com/search?find_desc=Coffee+%26+Tea&find_loc=Los+Angeles']
	
	
	def __init__(self, name=None, **kwargs): 
		self.projectName='yelp'
		self.baseURL = 'http://www.yelp.com'
		log=[]
		
		
		print 'Yelp Spider Started!!!'
		file_name = kwargs['file_name']
		self.download_delay = 10;
		self.start_urls = [kwargs["url"]];
		file = open(file_name, 'ab')
		self.writer = UnicodeWriter(file)
		self.writer.writerow(['Source_URL','Name','Phone_Number','Street','City','State','Website'])
		
		
	def parse(self, response):
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'GetList: '+response.url
			
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 			
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		next_page_link = None;
		reqs = [];
		try:
			next_page_link = "http://www.yelp.com" + hxs.select('.//a[@class="page-option prev-next next"]//@href').extract()[0].strip()
			req = Request(url=next_page_link, priority=2, callback=self.parse)
			reqs.append(req);
		except:
			pass;
		items = hxs.select('//div[contains(@class,"search-result natural-search-result")]')
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
					street_addr = item.select('.//address').extract()[0].strip().replace("<address>", "").replace("</address>", "").replace("<br>", ",").replace("\n", " ").replace("\r", " ").replace("\r\n", " ").strip();
					
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
			req = Request(url=url, priority=2, callback=self.getWebsite)
			req.meta["url"] = url;
			req.meta["name"] = name;
			req.meta["street_addr"] = street_addr;
			req.meta["locality"] = locality;
			req.meta["phone_no"] = phone_no;
			reqs.append(req);
			
			
		return reqs;
	
	def getWebsite(self, response):
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'GetList: '+response.url
		website = "";	
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 			
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		try:
			website = hxs.select('//div[@class="biz-website"]//a//text()')[0].extract().strip();
		except:
			pass
		url = response.request.meta["url"];
		name = response.request.meta["name"];
		street_addr = response.request.meta["street_addr"];
		locality = response.request.meta["locality"];
		phone_no = response.request.meta["phone_no"];
		info = [url,name,phone_no,street_addr + "," + locality,'', '', website]
		try:
			self.writer.writerow(info)
		except:
			pass;
	
		

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

