import os
import sys
import csv
import threading
import cPickle as pickle

def checkProxy(proxy):
	for l in os.popen("http_proxy=\""+proxy+"\" wget --spider --tries=3 --timeout=3 -S 'http://www.yellowpages.com' 2>&1 | grep 'HTTP/' | awk '{print $2}'"):
	        if l.find("200")>-1:
			print proxy+" Works!"
	                return True
	print proxy+" Fails!"
	return False


class proxyChecker(threading.Thread):
	def __init__(self,proxy,pList,Lock):
		self.proxy=proxy
		self.proxyList=pList
		self.threadLock=Lock
		threading.Thread.__init__(self)
	def run(self):
		if checkProxy(self.proxy):
			self.threadLock.acquire(1)
			self.proxyList.append(self.proxy)
			self.threadLock.release()


class proxyAllocator():
	def __init__(self,pCount,tCount=99999):
		self.ctr=0
		self.proxyList=[]
		self.pCount=pCount
		self.tCount=str(tCount)
		self.getProxyList()
		pickle.dump(self.proxyList,open("proxyList.p","wb"))
#		self.proxyList=pickle.load(open("proxyList.p","rb"))


	def getProxyList(self):
		self.ctr=0
		#Change this to change source of all proxies
		#Check for working proxies
		pcList=[]
		proxy_file = open('/home/easydeal/proxylist/latest_proxy_list.csv','rb')
		reader=csv.reader(proxy_file)
		threadLock = threading.Lock()
		for row in reader:
			proxy = row[0].strip()
			tempPC=proxyChecker(proxy,self.proxyList,threadLock)
			pcList.append(tempPC)
			tempPC.start()
		"""
		for p in self.cur.fetchall():
			tempPC=proxyChecker(p[0],self.proxyList,threadLock)
			pcList.append(tempPC)
			tempPC.start()
		"""	
		for pc in pcList:
			pc.join()
		print "Proxy List Generated!"	
	
	def getProxy(self):
#		print self.proxyList
		if (self.ctr/self.pCount < len(self.proxyList)):
			curProxy=self.proxyList[self.ctr/self.pCount]
			self.ctr=self.ctr+1
			if (self.ctr/self.pCount >= len(self.proxyList)):
				self.ctr=0
			print "Returning Proxy : " + curProxy
			return curProxy	
		print "Cannot Allocate any proxies!!!"
		# Send notification

		# goto sleep!
	
		# call getProxyList

		# return getProxy
		return


