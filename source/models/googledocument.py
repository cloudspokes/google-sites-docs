from google.appengine.ext import db
import hashlib
import logging

class GoogleDocument(db.Model):
	json        = db.StringProperty(required=False)
	siteName    = db.StringProperty(required=False)
	userAccount = db.StringProperty(required=False)
	
	@classmethod
	def new(cls,**kwds):
		''' Uniquely insert entry on the db '''
		_newobj = cls.get_or_insert(cls.keyName(**kwds),**kwds)
		return _newobj
	
	@classmethod
	def keyName(cls,**kwds):
		''' Return a keyname for the specified kwds using sha224 '''
		_keystring = ''
		for key in kwds: _keystring += (kwds.get(key) + '&')
		_keyname = hashlib.md5(_keystring).hexdigest()
		return _keyname
	


##############################################################
# Tests
##############################################################
class testGoogleDocument(object):
	def __init__(self):
		self.setUp()
		self.testNew()
		self.cleanUp()
	
	def testNew(self):
		initial_count = GoogleDocument.all().count()
		logging.info(initial_count)
		test_cases = [
			{ 'json' : '{ jsonString }',
			  'siteName' : 'abc',
			  'userAccount' : 'a@b.com' },	
			{ 'json' : '{ different jsonString }',
			  'siteName' : 'abc',
			  'userAccount' : 'a@b.com' },
			{ 'json' : '{ jsonString }',
			  'siteName' : 'abc',
			  'userAccount' : 'a@b.com' },			
			{ 'json' : '{ blaber blaber }',
			  'siteName' : 'abc',
			  'userAccount' : 'a@b.com' },
			{ 'json' : '',
			  'siteName' : 'abc',
			  'userAccount' : 'a@b.com' },		
			{ 'json' : '{ lalalala }',
			  'siteName' : 'abc',
			  'userAccount' : '' },		
			{ 'json' : '{ aasfas }',
			  'siteName' : '',
			  'userAccount' : 'a@b.com' }
		]
		test_result = 6 # db should have no duplicates
		for case in test_cases:
			newobj = GoogleDocument.new(json=case['json'],
					   		  	        siteName=case['siteName'],
							  	        userAccount=case['userAccount'])
			self.mockObjs.append(newobj)
			assert newobj.is_saved(), 'Failed to save to database'
		result = int(GoogleDocument.all().count())
		expected = int(test_result+initial_count)
		assert result is expected, 'Expected '+str(expected)+' got '+str(result)
	
	def setUp(self):
		self.mockObjs = []
	
	def cleanUp(self):
		for obj in self.mockObjs:
			obj.delete()
	

