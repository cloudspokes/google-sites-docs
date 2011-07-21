from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from xml.etree import ElementTree
from django.utils import simplejson
from models.googledocument import *
from helpers.helpers import *
import urllib
import logging
import os

HTTP_OK = 200

# TODO: add test for the handler class
class InventoryTaskHandler(webapp.RequestHandler):
	'''Handler for /inventory'''
	
	def __init__(self):
		self.docLocations = [ { 'tag' : 'a', 'attribute' : 'href' },
							  { 'tag' : 'iframe', 'attribute' : 'src' } ]
		self.templateName = 'inventory.html'
		self.maxResults = 0
		self.startIndex = 0
		self.feedURL = ''
		self.xmlfeed = ''
		self.feed = ''
		self.urlList = []
		self.oauthToken = ''
		self.siteURL = ''
		self.siteName = ''
		self.siteDomain = ''		
		self.userAccount = ''
	
	def post(self):
		''' Handles POST requests to /inventory '''
		self.userAccount = self.request.get('userAccount')
		self.siteDomain  = self.request.get('siteDomain')
		self.siteName    = self.request.get('siteName') or self.request.get('other')
		self.oauthToken  = self.request.get('oauthToken')
		self.maxResults  = self.request.get('maxResults') or 1
		self.startIndex  = self.request.get('startIndex') or 1
		
		self.getFeedURL()
		self.fetchFeed()
		if self.feedHasEntries():
			self.runTaskForNextFeed()
			self.collectDocsURLInFeed(self.feed)
			self.getSiteURLFrom(self.siteDomain,self.siteName)
			self.storeGoogleDocsURLsToDatabase()
	
	### Helper Methods
	def feedHasEntries(self):
		try:
			self.xmlfeed = ElementTree.fromstring(self.feed)
			return self.xmlfeed.findall('.//{http://www.w3.org/2005/Atom}entry')
		except:
			pass
			return False
	
	def runTaskForNextFeed(self):
		''' Run a new task that processes the next feed '''
		
		payload = {
			'siteName'    : self.siteName,
			'userAccount' : self.userAccount,
			'oauthToken'  : self.oauthToken,
			'siteDomain'  : self.siteDomain,
			'startIndex'  : int(self.startIndex) + int(self.maxResults),
			'maxResults'  : self.maxResults
		}
		queue = taskqueue.Queue('default')
		task = taskqueue.Task(url='/inventory_task',
							  method='POST',
							  params=payload)
		queue.add(task)
	
	def getSiteURLFrom(self,siteDomain,siteName):
		''' Puts the site url for the given siteDomain and siteName on self.siteURL '''
		
		baseURL = 'https://sites.google.com/'
		if siteDomain == 'site':
			baseURL += 'site/'
		else:
			baseURL += 'a/' + siteDomain + '/'
		self.siteURL = baseURL + siteName
		
	def fetchFeed(self):
		''' Puts the feed contents from feedURL on self.feed
		    Returns True on success
		    Writes out the content from fetch on failure'''
		result = urlfetch.fetch(self.feedURL)
		logging.info('fetching '+self.feedURL)
		if result.status_code == HTTP_OK:
			self.feed = result.content
			return True
		else:
			return False
	
	def getFeedURL(self):
		args = { 'max-results' : self.maxResults, 
		         'start-index' : self.startIndex,
				 'oauth_token' : self.oauthToken
		# full-text search, though not able to search the embedded docs on iframes
		#        'q'		   : '"docs.google.com"'
		}
		baseURL = 'https://sites.google.com/feeds/content/'
		self.feedURL = baseURL + self.siteDomain + '/' + self.siteName + '?' + urllib.urlencode(args)
	
	
	def collectDocsURLInFeed(self,feed):
		''' Appends google docs urls in self.feed to self.urlList '''
		try:
			self.xmlfeed = ElementTree.fromstring(feed)
			for location in self.docLocations:
				for link in self.xmlfeed.findall('.//{http://www.w3.org/1999/xhtml}'+location['tag']):
					linkURL = sanitizeGoogleDocsURL(link.get(location['attribute']))
					if linkURL:	self.urlList.append(linkURL)
		except:
			pass
			return
	
	def storeGoogleDocsURLsToDatabase(self):
		''' Stores all the urls in self.urlList into the Database '''
		for url in self.urlList:
			self.putGoogleDocURLToDatabase(url)
	
	def putGoogleDocURLToDatabase(self,docURL):
		''' Puts the docURL specified into the database as a json string
		    including the site name and the user account. Prevents duplicate entries '''
		jsonString = simplejson.dumps({ 'siteURL' : self.siteURL,
				   				        'docID'   : docURL
		})
		GoogleDocument.new(json=jsonString,
						   siteName=self.siteName,
				           userAccount=self.userAccount)
				
	


##############################################################
# Tests
##############################################################
class testInventoryTaskHandler(object):
	def __init__(self):
		self.setup()
		self.testGetSiteURLFrom()
		self.testCollectDocsURLInFeed()
	
	def setup(self):
		self.mockHandler = InventoryTaskHandler()
		assert self.mockHandler, "Failed to create mock object SiteSelectHandler"
		
		self.mockHandler.initialize(webapp.Request({}),webapp.Response())
		assert self.mockHandler.request, "Failed to initialize with request"
		assert self.mockHandler.response, "Failed to initialize with response"
	
	def testGetSiteURLFrom(self):
		test_cases = [
			{ 'siteDomain' : 'site', 'siteName' : 'abcd',
			  'out' : 'https://sites.google.com/site/abcd'},
			{ 'siteDomain' : 'example.com', 'siteName' : 'def',
			  'out' : 'https://sites.google.com/a/example.com/def'}
		]
		for case in test_cases:
			self.mockHandler.getSiteURLFrom(case['siteDomain'],case['siteName'])
			result = self.mockHandler.siteURL
			assert result == case['out'], str(case['out'])+' is expected; got '+str(result)
	
	def testCollectDocsURLInFeed(self):
		test_cases = [
			{ 'in' : '''<?xml version='1.0' encoding='UTF-8'?>
			<feed xmlns='http://www.w3.org/2005/Atom' xmlns:openSearch='http://a9.com/-/spec/opensearch/1.1/' xmlns:gAcl='http://schemas.google.com/acl/2007' xmlns:sites='http://schemas.google.com/sites/2008' xmlns:gs='http://schemas.google.com/spreadsheets/2006' xmlns:dc='http://purl.org/dc/terms' xmlns:batch='http://schemas.google.com/gdata/batch' xmlns:gd='http://schemas.google.com/g/2005' xmlns:thr='http://purl.org/syndication/thread/1.0'>
				<entry gd:etag='&quot;YD8peyY.&quot;'>
					<content type='xhtml'><div xmlns="http://www.w3.org/1999/xhtml"><table cellspacing="0" class="sites-layout-name-one-column sites-layout-hbox"><tbody><tr><td class="sites-layout-tile sites-tile-name-content-1"><div dir="ltr"><a href="/" /><div class="sites-embed-align-left-wrapping-off"><div class="sites-embed-border-on sites-embed sites-embed-full-width" style="width:100%;"><h4 class="sites-embed-title">coe 111 2010</h4><div class="sites-embed-object-title" style="display:none;">coe 111 2010</div><div class="sites-embed-content sites-embed-type-spreadsheet"><iframe src="http://spreadsheets.google.com/spreadsheet/loadredirect?chrome=false&amp;key=0Aon0ChOsT_BbdFp6aWd5cFRvM292aUNabTFPa1Roanc&amp;output=html&amp;pubredirect=true&amp;widget=true" width="100%" height="600" frameborder="0" id="1949721636" /></div></div></div><div class="sites-embed-align-left-wrapping-off"><div class="sites-embed-border-on sites-embed sites-embed-full-width" style="width:100%;"><h4 class="sites-embed-title">Guidelines_RCICT2011.docx</h4><div class="sites-embed-object-title" style="display:none;">Guidelines_RCICT2011.docx</div><div class="sites-embed-content sites-embed-type-writely"><iframe src="http://docs.google.com/document/preview?hgd=1&amp;id=1vHLqj_ldxqiJQ8S8H9plDvY2xjEtiYN9SZV31R8B0Ko" width="100%" height="600" frameborder="0" /></div></div></div><br /></div></td></tr></tbody></table></div></content>
				</entry>
				<entry gd:etag='&quot;YD4peyY.&quot;'>
					<content type='xhtml'><div xmlns="http://www.w3.org/1999/xhtml"><table cellspacing="0" class="sites-layout-name-one-column sites-layout-hbox"><tbody><tr><td class="sites-layout-tile sites-tile-name-content-1"><div dir="ltr"><div class="sites-embed-align-left-wrapping-off"><div class="sites-embed-border-on sites-embed" style="width:410px;"><h4 class="sites-embed-title">Plants We Eat: Nutrition &amp; Botany</h4><div class="sites-embed-object-title" style="display:none;">Plants We Eat: Nutrition &amp; Botany</div><div class="sites-embed-content sites-embed-type-presently"><iframe src="http://docs.google.com/present/embed?hl=en&amp;id=0AUhNMx8czWdzZGN2czZnNXdfNmhxNDdiOGYy&amp;size=s" width="410" height="342" frameborder="0" id="1831270098" /></div></div></div><br /></div></td></tr></tbody></table></div></content>
				</entry>
			</feed>''',
			  'out' : ['http://spreadsheets.google.com/spreadsheet/loadredirect?chrome=false&key=0Aon0ChOsT_BbdFp6aWd5cFRvM292aUNabTFPa1Roanc&output=html&pubredirect=true&widget=true',
			           'http://docs.google.com/document/preview?hgd=1&id=1vHLqj_ldxqiJQ8S8H9plDvY2xjEtiYN9SZV31R8B0Ko',
			           'http://docs.google.com/present/embed?hl=en&id=0AUhNMx8czWdzZGN2czZnNXdfNmhxNDdiOGYy&size=s']},
			{ 'in' : '' , 'out' : [] }
		]
		for case in test_cases:
			if not self.mockHandler.collectDocsURLInFeed(case['in']): logging.error('returned False')
			result = self.mockHandler.urlList
			assert result == case['out'], str(case['out'])+' is expected; got '+str(result)
			self.mockHandler.urlList = []
	
