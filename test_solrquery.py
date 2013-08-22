
import sys
import os
import time
import random
import string

from flask import Flask, render_template, render_template_string
from flask.ext.solrquery import FlaskSolrQuery

if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

class FlaskSolrTestCase(unittest.TestCase):
    
    def setUp(self):
        app = Flask(__name__, template_folder=os.path.dirname(__file__))
        app.debug = True
        app.config['TESTING'] = True
        app.config['SOLR_URL'] = 'http://httpbin.org/get'
        
        self.solr = FlaskSolrQuery(app)
        self.app = app

        self.resp_data = {
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
        
        
    def tearDown(self):
        
        self.solr = None
        self.app = None
        
    def test_00_query(self):

        def _monkey_patched(slf):
            return 200, self.resp_data
        
        self.solr._get_raw_response = _monkey_patched

        req = self.solr.create_request("black holes")
        resp = self.solr.get_response(req)
        self.assertEqual(resp.get_hits(), 13)
    
if __name__ == '__main__':
    unittest.main()
