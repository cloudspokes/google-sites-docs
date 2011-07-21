from google.appengine.ext import webapp
from google.appengine.api import taskqueue
from google.appengine.ext.webapp import template
from models.googledocument import *
import os
import logging

class DatastoreViewerHandler(webapp.RequestHandler):
    '''Handler for /datastore_viewer '''
    
    def __init__(self):
        self.templateName = 'datastoreviewer.html'
    
    def get(self):
        ''' Handles POST requests to /inventory '''
        self.renderTemplate()
    
    
    def renderTemplate(self):
        entities = GoogleDocument.all().fetch(GoogleDocument.all().count())
        
        template_values = {
            'entities' : entities,
        }
        path = os.path.join(os.path.dirname(__file__), self.templateName)
        self.response.out.write(template.render(path,template_values))
	