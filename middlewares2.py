# Importing base64 library because we'll need it ONLY in case if the proxy we are going to use requires authentication
import base64
import sys
from proxyLib import *
from scrapy.conf import settings
 
# Start your middleware class

class ProxyMiddleware(object):
    def __init__(self):
	self.pa=proxyAllocator(1,350)

    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy
        request.meta['proxy'] = "http://"+str(self.pa.getProxy())
		print request.meta['proxy'], request.url 
        # Use the following lines if your proxy requires authentication
	        #proxy_user_pass = "USERNAME:PASSWORD"
        # setup basic authentication for the proxy
		#encoded_user_pass = base64.encodestring(proxy_user_pass)
		#request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
