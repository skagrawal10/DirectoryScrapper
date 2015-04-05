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
	
	name='yellowpages'
	#start_urls = ['http://www.yellowpages.com/search?search_terms=Plumber&geo_location_terms=New+York%2C+NY']
	download_delay = 2
	
	def __init__(self, name=None, **kwargs): 
		self.projectName='yellowpages'
		self.baseURL = 'http://www.yellowpages.com'
		log=[]
	
		self.download_delay = 10;
		self.start_urls = [kwargs["url"]];
		file_name = kwargs['file_name']
		file = open(file_name, 'ab')
		self.writer = UnicodeWriter(file)
		
		self.writer.writerow(['Source_URL','Name','Phone_Number','Street','City','State','ZIP','Website'])
		
		
	def parse1(self, response):
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'Getdetails: '+response.url#, 'PROXY: '+str(response.meta['proxy'])
		
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		
		no_results = re.findall('Showing.*?1-.*?of(.*?)<',data)
		if len(no_results)>0:
			no_results = no_results[0].replace('"', '').strip()
			print '#results: '+str(no_results)
		else:
			no_results = 0
			print 'NO results: '+response.url
		
		no_results = int(no_results)		
		no_pages = math.ceil(no_results/30.0)
		if no_pages == 0:
			no_pages = 1
		print '#Pages:',no_pages
		
		reqs = []
		page_no=1
		while page_no<=no_pages:			
			page_url = response.url+'&page='+str(page_no)
			req = Request(url=page_url, priority=2, callback=self.getList)
			print page_url;
			reqs.append(req)
			page_no += 1
			#if page_no>2:
			#	break;
		return reqs

		
	def parse(self, response):
		if str(response.status) == '403':
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'GetList: '+response.url
			
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 			
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		reqs = [];
		next_page_link = None;
		try:
			next_page_link = self.baseURL +	hxs.select('//a[@class="next ajax-page"]//@href')[0].extract();
			print "Next Page URL - " + next_page_link;
			nnext_page_link = next_page_link.replace("#", "&").replace("refinements=facet_clicked%3A", "");
			req = Request(url=next_page_link, priority=2, callback=self.parse)
			reqs.append(req);
		except:
			pass;
		
		
		items = hxs.select('//div[@class="search-results organic"]//div[@class="v-card"]')
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
				url = self.baseURL + item.select('.//h3/a/@href').extract()[0].strip()
				try:
					name = item.select('.//a[@itemprop="name"]//text()').extract()[0].strip()
				except:
					pass;
				try:
					street_addr = item.select('.//span[@itemprop="streetAddress"]//text()').extract()[0].strip()
				except:
					pass;
				try:
					locality = item.select('.//span[@itemprop="addressLocality"]//text()').extract()[0].strip(',').strip()
				except:
					pass;
				try:
					region = item.select('.//span[@itemprop="addressRegion"]//text()').extract()[0].strip()
				except:
					pass;
				try:
					postal = item.select('.//span[@itemprop="postalCode"]//text()').extract()[0].strip()
				except:
					pass;
				try:
					phone_no = item.select('.//div[@itemprop="telephone"]//text()').extract()[0].strip()
				except:
					pass;
				try:
					website = item.select('.//a[@class="track-visit-website"]/@href').extract()[0].strip()
				except:
					pass
			except:
				pass
				
			info = [url,name,phone_no,street_addr,locality,region,postal,website]
			self.writer.writerow(info)
			
		return reqs	
		
	
	def handler(self, signum, frame):
		print "Parsing function taking forever!!"
		raise Exception("end of time")
	
	def error(self, response):
		print 'ERROR: '+response.url
		print 'ERROR code: '+str(response.status)
		
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

