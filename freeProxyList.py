import os
import csv
import traceback
import sys
import urllib2 
from scrapy.selector import HtmlXPathSelector


class freeProxyListSpider():
	name='freeproxylist'

	#Get the homepage
	start_urls = ['http://www.free-proxy-list.net']
	
	def __init__(self, **kwargs):
		proxyList = []
		
		try:
			url = self.start_urls[0]
			self.urlLibGetCall("http", url, "proxy_page.html")
			html = open("proxy_page.html", "r").read()
			hxs = HtmlXPathSelector(text = html)
			trs = hxs.select('//table[@id="proxylisttable"]//tbody/tr')
			for tr in trs:
				tds = tr.select('.//td/text()').extract()
				ip = tds[0].strip()
				port = tds[1].strip()
				type = tds[4].strip()
				if type == 'elite proxy':
					proxyList.append(ip + ':' + port)
		except:
			traceback.print_exc()
			pass
	
		if len(proxyList) >= 10:
			self.out_file = open('latest_proxy_list.csv', 'wb')
			self.writer = csv.writer(self.out_file)
			for proxy in proxyList:
				self.writer.writerow([proxy])
			self.out_file.close()
			
			
		
	def myWgetCall(self, connection_type, url, post_data, output_file):
		trial = 0
		gotResponse = False
		while (trial < 1 and not gotResponse):
			trial += 1
			cmd = "wget --timeout=30 --no-check-certificate --tries=2 '"+url+"' -U 'Mozilla/5.0 (Windows NT 5.1; rv:13.0) Gecko/20100101 Firefox/13.0.1' -O " + output_file
			if post_data != "":
				cmd += ' --post-data="' + post_data + '"'
			os.system(cmd)
			try:
				f = open(output_file, 'r')
				text = f.read()
				f.close()
				if text.strip() != '':
					gotResponse = True
			except:
				traceback.print_exc()
				pass
		return
		
	def urlLibGetCall(self, connection_type, url, output_file):	
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		the_page = response.read()
		f = open(output_file, "wb")
		f.write(the_page);

		
if __name__ == '__main__':
	spider = freeProxyListSpider()
