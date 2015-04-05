# Scrapy settings for yellowpages project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'yellowpages'


SPIDER_MODULES = ['yellowpages.spiders']
NEWSPIDER_MODULE = 'yellowpages.spiders'
USER_AGENT="Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1"
#DOWNLOADER_MIDDLEWARES = {
#    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
#    'middlewares.ProxyMiddleware': 100,
#}

DOWNLOADER_MIDDLEWARES = {
    'middlewares.ProxyMiddleware': 543,
}

CONCURRENT_REQUESTS=1
CONCURRENT_REQUESTS_PER_DOMAIN=1
DOWNLOAD_DELAY=10

PROJECT_NAME='nielsen'
