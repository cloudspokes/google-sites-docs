from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from django.utils import simplejson
import logging
import urllib
import sys
import os

HTTP_OK = 200

class SiteSelectHandler(webapp.RequestHandler):
	''' Handler for /site_select '''
		
	def __init__(self):
		self.userAccount = ''
		self.siteDomain = ''
		self.oauthToken = ''
		self.accessibleSites = []
		self.fetchContent = ''
		self.fetchStatus  = 0
		self.templatename = 'siteselect.html'
	
	def post(self):
		self.userAccount = self.request.get('userAccount')
		self.siteDomain  = self.request.get('siteDomain')
		self.oauthToken  = self.request.get('oauthToken')
		self.fetchSitesFeed()
		self.getAccessibleSitesFromFeed(self.fetchContent)
		self.renderTemplate()
	
	### Helper methods
	def renderTemplate(self):
		''' Write to the response using a template '''
		if self.fetchStatus == HTTP_OK:
			template_values = {
				'args'  : { 'userAccount' : self.userAccount,
	  			            'siteDomain'  : self.siteDomain,
	  			            'oauthToken'  : self.oauthToken },
				'sites' : self.accessibleSites
			}
			path = os.path.join(os.path.dirname(__file__), self.templatename)
			self.response.out.write(template.render(path,template_values))
		else:
			self.response.out.write(self.fetchContent)
	
	def fetchSitesFeed(self):
		''' Puts the accessible sites feed (from sites API) on self.fetchResult '''
		baseURL = 'https://sites.google.com/feeds/site/' + self.siteDomain
		args    = { 'alt'         : 'json',
			 	    'oauth_token' : self.oauthToken
		}
		url = baseURL + '?' + urllib.urlencode(args)
		result = urlfetch.fetch(url)
		self.fetchContent = result.content
		self.fetchStatus = result.status_code
	
	def getAccessibleSitesFromFeed(self,feed):
		''' Extracts the site names from feed. Feed is assumed to be a json string '''
		try:
			jsonFeed = simplejson.loads(feed)
			for entry in jsonFeed['feed']['entry']:
				self.accessibleSites.append(entry['sites$siteName']['$t'])
		except:
			logging.error('exception: ' + str(sys.exc_info()[1]))
			pass
	


##############################################################
# Tests
##############################################################

class testSiteSelectHandler(object):
	def __init__(self):
		self.mockHandler  = SiteSelectHandler()
		assert self.mockHandler, "Failed to create mock object SiteSelectHandler"
	
		self.mockHandler.initialize(webapp.Request({}),webapp.Response())
		assert self.mockHandler.request, "Failed to initialize with request"
		assert self.mockHandler.response, "Failed to initialize with response"
		self.testGetAccessibleSitesFromFeed()
	
	def testGetAccessibleSitesFromFeed(self):
		test_cases = [
			{ 'feed' : r'', 'out' : [] },
			{ 'feed' : r'''<html><head><title>Token invalid - Invalid AuthSub token.</title></head><body bgcolor="#ffffff" text="#000000"><h1>Token invalid - Invalid AuthSub token.</h1><h2>Error 401</h2></body></html>''',
			  'out'  : [] },
			{ 'feed' : r'''{"version":"1.0","encoding":"UTF-8","feed":{"xmlns":"http://www.w3.org/2005/Atom","xmlns$openSearch":"http://a9.com/-/spec/opensearch/1.1/","xmlns$gAcl":"http://schemas.google.com/acl/2007","xmlns$sites":"http://schemas.google.com/sites/2008","xmlns$gs":"http://schemas.google.com/spreadsheets/2006","xmlns$dc":"http://purl.org/dc/terms","xmlns$batch":"http://schemas.google.com/gdata/batch","xmlns$gd":"http://schemas.google.com/g/2005","xmlns$thr":"http://purl.org/syndication/thread/1.0","id":{"$t":"https://sites.google.com/feeds/site/site"},"updated":{"$t":"2011-05-27T12:17:15.383Z"},"title":{"$t":"Site"},"link":[{"rel":"http://schemas.google.com/g/2005#feed","type":"application/atom+xml","href":"https://sites.google.com/feeds/site/site"},{"rel":"http://schemas.google.com/g/2005#post","type":"application/atom+xml","href":"https://sites.google.com/feeds/site/site"},{"rel":"self","type":"application/atom+xml","href":"https://sites.google.com/feeds/site/site?alt\u003djson"}],"generator":{"version":"1","uri":"http://sites.google.com","$t":"Google Sites"},"openSearch$startIndex":{"$t":"1"},"entry":[{"gd$etag":"\"YDkpeyY.\"","id":{"$t":"https://sites.google.com/feeds/site/site/t3sts1t351"},"updated":{"$t":"2011-05-27T09:15:30.136Z"},"app$edited":{"xmlns$app":"http://www.w3.org/2007/app","$t":"2011-05-27T09:15:30.136Z"},"title":{"$t":"t3sts1t351"},"summary":{"$t":""},"link":[{"rel":"alternate","type":"text/html","href":"https://sites.google.com/site/t3sts1t351/"},{"rel":"http://schemas.google.com/acl/2007#accessControlList","type":"application/atom+xml","href":"https://sites.google.com/feeds/acl/site/site/t3sts1t351"},{"rel":"self","type":"application/atom+xml","href":"https://sites.google.com/feeds/site/site/t3sts1t351"},{"rel":"edit","type":"application/atom+xml","href":"https://sites.google.com/feeds/site/site/t3sts1t351"}],"sites$siteName":{"$t":"t3sts1t351"},"sites$theme":{"$t":"iceberg"}},{"gd$etag":"\"YD4peyY.\"","id":{"$t":"https://sites.google.com/feeds/site/site/testingteh333"},"updated":{"$t":"2011-05-25T08:00:02.893Z"},"app$edited":{"xmlns$app":"http://www.w3.org/2007/app","$t":"2011-05-25T08:00:02.893Z"},"title":{"$t":"testingteh333"},"summary":{"$t":""},"link":[{"rel":"alternate","type":"text/html","href":"https://sites.google.com/site/testingteh333/"},{"rel":"http://schemas.google.com/acl/2007#accessControlList","type":"application/atom+xml","href":"https://sites.google.com/feeds/acl/site/site/testingteh333"},{"rel":"self","type":"application/atom+xml","href":"https://sites.google.com/feeds/site/site/testingteh333"},{"rel":"edit","type":"application/atom+xml","href":"https://sites.google.com/feeds/site/site/testingteh333"}],"sites$siteName":{"$t":"testingteh333"},"sites$theme":{"$t":"iceberg"}}]}}''',
			  'out'  : [ u't3sts1t351', u'testingteh333' ] }
		]
		
		for case in test_cases:	
			self.mockHandler.getAccessibleSitesFromFeed(case['feed'])
			result = self.mockHandler.accessibleSites
			assert case['out'] == result, "Expected "+str(case['out'])+". Got "+str(result)
	
