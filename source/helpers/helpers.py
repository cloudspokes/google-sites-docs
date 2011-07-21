import re

def sanitizeGoogleDocsURL(url):
	''' Returns empty string if the url given is not on google docs
		and not a document or presentation or similar '''
	
	regexMatch = '^http[s]?://(docs|spreadsheets).google.com/(?!support).+'
	if not re.match(regexMatch,str(url)): return ''
	return url

##############################################################
# Tests
##############################################################
def testSanitizeGoogleDocsURL():
	test_cases = [ 
		{ 'in' : 'http://',                               'out' : ''},
        { 'in' : 'https://',                              'out' : ''},
        { 'in' : 'http://docs.google.com',                'out' : ''},
        { 'in' : 'https://docs.google.com',               'out' : ''},
        { 'in' : 'http://docs.google.com/',               'out' : ''},
        { 'in' : 'https://docs.google.com/',              'out' : ''},
        { 'in' : 'http://docs.google.com/support',        'out' : ''},
        { 'in' : 'https://docs.google.com/support',       'out' : ''},
        { 'in' : 'http://docs.google.com/support?asfa3',  'out' : ''},
        { 'in' : 'https://docs.google.com/support?asfa3', 'out' : ''},
        { 'in' : 'abcd',                                  'out' : ''},
        { 'in' : '',                                      'out' : ''},
        { 'in' : 'http://docs.google.com/present/view?id=dfvwdtqp_119gtz52dg3',
         'out' : 'http://docs.google.com/present/view?id=dfvwdtqp_119gtz52dg3'},
        { 'in' : 'https://docs.google.com/Doc?id=dgdwkz9w_65dzbp67gs',
         'out' : 'https://docs.google.com/Doc?id=dgdwkz9w_65dzbp67gs'},
	]
	
	for case in test_cases:
		result = sanitizeGoogleDocsURL(case['in'])
		assert result is case['out'], str(case['out'])+' is expected; got '+str(result)
