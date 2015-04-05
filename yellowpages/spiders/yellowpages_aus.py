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
	
	name='yellowpages_aus'
	#start_urls = ['http://www.yellowpages.com.au/search/listings?clue=restaurants&locationClue=australia&lat=&lon=&referredBy=UNKNOWN&selectedViewMode=list&eventType=refinement&refinedCategory=42730']

	
	
	def __init__(self, name=None, **kwargs): 
		self.projectName='yellowpages'
		self.baseURL = 'http://www.yellowpages.com.au/'
		log=[]
		self.download_delay = 10;
		self.start_urls = [kwargs["url"]];
		
		print 'Yellowpages Spider Started!!!'
		print self.start_urls;
		file_name = kwargs['file_name']
		file = open(file_name, 'ab')
		self.writer = UnicodeWriter(file)
		
		
		
		
	def parse1(self, response):
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
		page_links = hxs.select('//a[@class="button button-pagination navigation"]//@href')[0].extract()
		req = Request(url=url, priority=2, callback=self.parse)
		reqs.append(req);
		return reqs

		
	def parse(self, response):
		print "Inside Parse"
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'GetList: '+response.url
			
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 			
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		reqs = []
		list1 = hxs.select('//div[@class="cell in-area-cell middle-cell"]//div[contains(@class,"listing-search")]')
		
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
				url = 'http://www.yellowpages.com.au' + card.select('.//a[@class="listing-name"]/@href').extract()[0].strip()
				print "URL " + url;
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
			obj = [url, name, phone, address, suburb, "", website, email];
			self.writer.writerow(obj);
			
		
		page_links = hxs.select('//a[@class="button button-pagination navigation"]//text()');
		index = 0;
		next_page_link = None;
		for link in page_links:
			text = link.extract().strip();
			if "Next" in text:
				next_page_link = self.baseURL +	hxs.select('//a[@class="button button-pagination navigation"]//@href')[index].extract();
				break;
			index += 1
		if next_page_link == None:
			return;
		print "Next Page URL - " + next_page_link;
		req = Request(url=next_page_link, priority=2, callback=self.parse)
		reqs.append(req);
		return reqs	
		#return
		
	
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

