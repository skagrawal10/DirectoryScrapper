import os
import sys
from threading import Thread
import time
import datetime
import csv
from freeProxyList import *

f = open("input.txt", "r");
content = f.readlines();
base_urls = [];
for line in content:
	if line.strip() != "":
		print line;	
		base_urls.append(line.replace("\n", "").replace("\r", ""));

print "Getting updated proxy lists"			
spider = freeProxyListSpider();
print "Proxy list is updated successfully"
now = datetime.datetime.now()
file_date = now.strftime('%Y%m%d')
file_name = "output_data_" + file_date + ".csv";
file = open(file_name, 'wb')
writer = csv.writer(file)
writer.writerow(['Source_URL','Name','Phone_Number','Street','City','State','Website', 'Email'])
#writer.writerow(['http://www.yellowpages.com.au/vic/ringwood/service-today-plumbing-heating-cooling-14776738-listing.html?referredBy=www.yellowpages.com.au&context=businessTypeSearch', 'Service Today Plumbing Heating & Cooling', '(03) 9816 3829', 'Ringwood VIC 3134', 'Ringwood VIC', '', 'http://www.servicetoday.com.au', 'info@servicetoday.com.au']);
file.close();
#writer.writerow(["http://www.yellowpages.com.au/vic/ringwood/service-today-plumbing-heating-cooling-14776738-listing.html?referredBy=www.yellowpages.com.au&context=businessTypeSearch","Service Today Plumbing", "Heating  & Cooling","(03) 9816 3829","Ringwood VIC 3134 Ringwood VIC",,"http://www.servicetoday.com.au,info@servicetoday.com.au"])



for url in base_urls:
	if "yellowpages.com.au" in url:
		siteName = "yellowpages_aus"
	elif "yellow.co.nz" in url:
		siteName = "yellowpages_nz"
	elif "yellowpages.com" in url:
		siteName = "yellowpages"
	elif "yelp.com" in url:
		siteName = "yelp"
	url = url.replace("#", "&");
	print url;
	cmd = 'copy /Y ' + siteName + '.py "' + "yellowpages" + '\\spiders\\' + siteName + '.py"';
	print cmd;
	#continue;
	os.system(cmd)
	cmd = 'scrapy crawl ' + siteName + ' -a url="' + url + '" -a file_name="' + file_name + '"'
	os.system(cmd)
	
	
	
print 'Parsing Done!!!'

