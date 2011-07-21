from google.appengine.ext import webapp
from google.appengine.api import taskqueue
from google.appengine.ext.webapp import template
import os

class InventoryHandler(webapp.RequestHandler):
	'''Handler for /inventory. Creates an offline task to process the request'''
	
	def __init__(self):
		self.templateName = 'inventory.html'
		self.userAccount = ''
		self.siteDomain = ''
		self.siteName = ''
		self.oauthToken = ''
	
	def post(self):
		''' Handles POST requests to /inventory '''
		self.userAccount = self.request.get('userAccount')
		self.siteDomain  = self.request.get('siteDomain')
		self.siteName    = self.request.get('siteName') or self.request.get('other')
		self.oauthToken  = self.request.get('oauthToken')
		payload = {
			'siteName'    : self.siteName,
			'userAccount' : self.userAccount,
			'oauthToken'  : self.oauthToken,
			'siteDomain'  : self.siteDomain
		}
		queue = taskqueue.Queue('default')
		task = taskqueue.Task(url='/inventory_task',
		                      method='POST',
		                      params=payload)
		queue.add(task)
		self.renderTemplate()
	
	def renderTemplate(self):
		template_values = {
			'siteDomain' : self.siteDomain,
			'siteName'   : self.siteName
		}
		path = os.path.join(os.path.dirname(__file__), self.templateName)
		self.response.out.write(template.render(path,template_values))
	
