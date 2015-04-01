import os
import sys
from threading import Thread
import time
import datetime
import csv
from freeProxyList import *

base_urls = ["http://yellow.co.nz/new-zealand/cafes/?what=Cafes&where=new-zealand"]
'''
["http://www.yelp.com/search?find_desc=Coffee+%26+Tea&find_loc=Los+Angeles", 
 "http://yellow.co.nz/new-zealand/cafes/?what=Cafes&where=new-zealand", 
"http://www.yellowpages.com.au/search/listings?clue=restaurants&locationClue=australia&lat=&lon=&referredBy=UNKNOWN&selectedViewMode=list&eventType=refinement&refinedCategory=42730",
"http://www.yellowpages.com/search?search_terms=cafe&geo_location_terms=Los+Angeles%2C+CA"
];
			'''
print "Getting updated proxy lists"			
spider = freeProxyListSpider();
print "Proxy list is updated successfully"
now = datetime.datetime.now()
file_date = now.strftime('%Y%m%d')
file_name = "output_data_" + file_date + ".csv";
file = open(file_name, 'wb')
writer = csv.writer(file)
writer.writerow(['Source_URL','Name','Phone_Number','Street','City','State','Website'])
	
for url in base_urls:
	if "yellowpages.com.au" in url:
		siteName = "yellowpages_aus"
	elif "yellow.co.nz" in url:
		siteName = "yellowpages_nz"
	elif "yellowpages.com" in url:
		siteName = "yellowpages"
	elif "yelp.com" in url:
		siteName = "yelp"
	
	cmd = 'copy /Y ' + siteName + '.py "' + "yellowpages" + '\\spiders\\' + siteName + '.py"';
	print cmd;
	#continue;
	os.system(cmd)
	os.system('scrapy crawl ' + siteName + ' -a file_name="' + file_name + '"')
	writer.writerow([url, ""]);
	
	
print 'Parsing Done!!!'

