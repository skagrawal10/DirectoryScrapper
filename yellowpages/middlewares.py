# Importing base64 library because we'll need it ONLY in case if the proxy we are going to use requires authentication
import base64
import sys
from proxyLib import *
from scrapy.conf import settings
 
# Start your middleware class
class ProxyMiddleware(object):
	def __init__(self):
		self.pa=proxyAllocator(1,100)

    # overwrite process request
	def process_request(self, request, spider):
		request.meta['proxy'] = "http://"+str(self.pa.getProxy())

        
