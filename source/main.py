#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from handlers.inventory import *
from handlers.siteselect import *
from handlers.inventorytask import *
from handlers.datastoreviewer import *
import os

# Go here first to get token:
# https://accounts.google.com/o/oauth2/auth?response_type=token&redirect_uri=http://localhost:8080/oauth2callback&client_id=744954785486.apps.googleusercontent.com&scope=https://sites.google.com/feeds/

class MainHandler(webapp.RequestHandler):
	''' Handler for / '''
	
	def __init__(self):
		self.templatename = 'index.html'
	
	def get(self):
		path = os.path.join(os.path.dirname(__file__), self.templatename)
		self.response.out.write(template.render(path,{}))
	


##############################################################
# Functions
##############################################################

def main():
	util.run_wsgi_app(application)


def runTests():
	''' Run the implemented tests. Will assert if failed a test case '''
	testSanitizeGoogleDocsURL()
	testSiteSelectHandler()
	testGoogleDocument()
	testInventoryTaskHandler()
	logging.info('tests passed')


if __name__ == '__main__':
	application = webapp.WSGIApplication([('/', MainHandler),
	                                      ('/inventory',InventoryHandler),
										  ('/inventory_task',InventoryTaskHandler),
										  ('/site_select',SiteSelectHandler),
                                          ('/datastore_viewer',DatastoreViewerHandler)],
	                                     debug=True)
	runTests()
	main()
