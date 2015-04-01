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
	
	name='yellowpages'
	start_urls = ['http://www.yellowpages.com']
	download_delay = 2
	
	def __init__(self, name=None, **kwargs): 
		#BaseSpider.__init__(self,name) 
		
		self.projectName='yellowpages'
		self.baseURL = 'http://www.yellowpages.com/search?search_terms=cafe&geo_location_terms=Los+Angeles%2C+CA'
		log=[]
	
		MAX_download_delay = 10
		print 'Yellowpages Spider Started!!!'

		now = datetime.datetime.now()
		file_date = now.strftime('%Y%m%d')

		file = open('yellowpages_' + self.selected_tag.replace(' ', '_') + '_' + file_date+'.csv', 'w')
		self.writer = csv.writer(file)
		
		self.writer.writerow(['Source_URL','Name','Phone_Number','Street','City','State','ZIP','Website'])
		
		

		
	def parse1(self,response):
		print 'Parse started!'
		

		
	def parse(self, response):
		if str(response.status) == '403':
			#self.mysendEmail(['aagrawal@operasolutions.com','varun.gagneja@opersolutions.com','anurag.gupta@operasolutions.com'], str( str('[Neilsen] Site:')+ str(self.name) + str(' proxoies are being blocked')))
			raise CloseSpider('proxy blocked')
			sys.exit(0)

		self.num_zips_completed += 1
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
		page_links = hxs.select('//div[@class="button-pagination-container"]/a/@href').extract()
		for link in page_links[:-1]:
			url = 'https://www.yellowpages.com.au' + link
			reqs.append(url);
		return reqs

		
	def getList(self, response):
		if str(response.status) == '403':
			#self.mysendEmail(['aagrawal@operasolutions.com','varun.gagneja@opersolutions.com','anurag.gupta@operasolutions.com'], str( str('[Neilsen] Site:')+ str(self.name) + str(' proxoies are being blocked')))
			raise CloseSpider('proxy blocked')
			sys.exit(0)
		print 'GetList: '+response.url
		self.zip_writer.writerow([response.meta['searchstring']])
		
		res_text = response.body_as_unicode().encode('ascii', 'ignore') 			
		data = res_text.replace('\n', ' ').replace('\r', ' ').replace('&amp;', '&').replace('\t', '')
		hxs = HtmlXPathSelector(response)
		
		name = ""
		phone_no=""
		street_addr=""
		locality=""
		region=""
		postal=""
		website=""
		url = ""
		
		items = hxs.select('//div[@class="search-results organic"]//div[@class="v-card"]')
		for item in items:
			try:
				url = self.baseURL + item.select('.//h3/a/@href').extract()[0].strip()
				name = item.select('.//span[@itemprop="name"]//text()').extract()[0].strip()
				street_addr = item.select('.//span[@itemprop="streetAddress"]//text()').extract()[0].strip()
				locality = item.select('.//span[@itemprop="addressLocality"]//text()').extract()[0].strip(',').strip()
				region = item.select('.//span[@itemprop="addressRegion"]//text()').extract()[0].strip()
				postal = item.select('.//span[@itemprop="postalCode"]//text()').extract()[0].strip()
				phone_no = item.select('.//li[@itemprop="telephone"]//text()').extract()[0].strip()
				try:
					website = item.select('.//a[@class="track-visit-website"]/@href').extract()[0].strip()
				except:
					pass
			except:
				pass
			info = [url,name,phone_no,street_addr,locality,region,postal,website]
			self.writer.writerow(info)
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

