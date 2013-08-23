
import sys
import os
import time
import random
import string
from copy import deepcopy
from mock import patch
from contextlib import contextmanager

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

class FakeSolrHttpResponse(object):
    
    DEFAULT_DATA = {
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
    def __init__(self, data=None, status_code=200):
        self.status_code = status_code
        self.data = data
        if self.data is None:
            self.data = self.DEFAULT_DATA

    def json(self):
        return self.data

@contextmanager
def fake_solr_http_response(data=None, status_code=200):
    def fake_send(*args, **kwargs):
        return FakeSolrHttpResponse(data, status_code)
    mocked_send = patch("flask_solrquery.requests.sessions.Session.send", fake_send)
    mocked_send.start()
    yield
    mocked_send.stop()
            
class FlaskSolrTestCase(unittest.TestCase, fixtures.TestWithFixtures):
    
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

        with fake_solr_http_response():
            req = self.solr.create_request("black holes")
            resp = self.solr.get_response(req)
            self.assertEqual(resp.get_hits(), 13)
        
    def test_01_reqest_context(self):
        
        with self.app.test_request_context('/'):
            with fake_solr_http_response():
                resp = solr.query("black holes")
                self.assertEqual(resp.get_hits(), 13)
        
        
if __name__ == '__main__':
    unittest.main()
