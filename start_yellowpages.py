import os
import sys
from threading import Thread
import time

siteName='yellowpages'

tags = ['plumbing']
cmd = 'copy /Y ' + siteName + '.py "' + siteName + '\\spiders\\' + siteName + '.py"';
print cmd;
os.system(cmd)

for tag in tags:
	os.system('scrapy crawl ' + siteName + ' -a category="' + tag + '"')
	break
	
print 'Parsing Done!!!'

