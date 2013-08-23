
import sys
import os
import time
import random
import string
from copy import deepcopy
from mock import Mock, patch

FIXTURES_OK = True
try:
    import fixtures
except ImportError:
    print "fixtures library not found. some tests will be skipped"
    FIXTURES_OK = False
    
from flask import Flask, render_template, render_template_string
from flask.ext.solrquery import FlaskSolrQuery, SearchResponseMixin, solr

if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

class FlaskSolrTestCase(unittest.TestCase):
    
    DEFAULT_RESPONSE = {
             "responseHeader":{
               "status":0,
               "QTime":1,
               "params":{ "indent":"true", "wt":"json", "q":"foo"}},
             "response":{
                "numFound":13,
                "start":0,
                "docs":[ 
                        { "id": 1 }, 
                        { "id": 2 }, 
                        { "id": 3 }, 
                        { "id": 4 }, 
                        { "id": 5 }, 
                        { "id": 6 }, 
                        { "id": 7 }, 
                        { "id": 8 }, 
                        { "id": 9 }, 
                        { "id": 10 }, 
                        { "id": 11 }, 
                        { "id": 12 }, 
                        { "id": 13 }, 
            ]}}
    
    def setUp(self):
        app = Flask(__name__, template_folder=os.path.dirname(__file__))
        app.debug = True
        app.config['TESTING'] = True
        app.config['SOLRQUERY_URL'] = 'http://httpbin.org/get'
        
        self.solr = FlaskSolrQuery(app)
        self.app = app
        
    def tearDown(self):
        
        self.solr = None
        self.app = None
        
    def test_00_query(self):

        req = self.solr.create_request("black holes")
        resp = self.solr.get_response(req)
        self.assertEqual(resp.get_hits(), 13)
        
    def test_01_reqest_context(self):
        
        with self.app.test_request_context('/'):
            resp = solr.query("black holes")
            self.assertEqual(resp.get_hits(), 13)
        
if __name__ == '__main__':
    unittest.main()
