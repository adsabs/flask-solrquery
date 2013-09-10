
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
from flask.ext.solrquery import FlaskSolrQuery, \
                                SearchResponseMixin, \
                                solr, \
                                SearchRequest

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
    def __init__(self, request, data=None, status_code=200):
        self.request = request
        self.status_code = status_code
        self.data = data
        if self.data is None:
            self.data = self.DEFAULT_DATA

    def json(self):
        return self.data

@contextmanager
def fake_solr_http_response(data=None, status_code=200):
    def fake_send(session_self, request, *args, **kwargs):
        return FakeSolrHttpResponse(request, data, status_code)
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
        
    def test_02_solr_request_http_method(self):
        req = SearchRequest("foo")
        prepared = req.prepare("http://example.com/select")
        self.assertEqual(prepared.method, 'GET')
        prepared = req.prepare("http://example.com/select", method='POST')
        self.assertEqual(prepared.method, 'POST')

        self.app.config['SOLRQUERY_HTTP_METHOD'] = 'POST'
        with self.app.test_request_context():
            with fake_solr_http_response():
                resp = solr.query("black holes")
                self.assertEqual(resp.request.prepared.method, 'POST')
        
class SolrTestCase(unittest.TestCase):

    def test_solr_request_defaults(self):
        req = SearchRequest("foo")
        self.assertIn('q', req.params)
        self.assertEqual(req.params['q'], "foo")
        self.assertEqual(req.params['wt'], "json")
        
    def test_solr_request_constructor_overrides(self):
        req = SearchRequest("foo", foo='fez', bar="baz")
        self.assertEqual(req.params['foo'], 'fez')
        self.assertEqual(req.params['bar'], 'baz')
        
    def test_solr_request_setters(self):
        req = SearchRequest("foo")   
        req.set_fields(['foo','bar'])
        expected = ['foo','bar']
        self.assertEqual(set(req.get_fields()), set(expected))
        req.set_rows(100)
        self.assertEqual(req.params.rows, 100)
        req.set_start(10)
        self.assertEqual(req.params.start, 10)
        req.set_sort("bar", "desc")
        self.assertEqual(req.params.sort, "bar desc")
        self.assertEqual(req.get_sort(), [('bar','desc')])
        req.set_sort("baz", "asc")
        self.assertEqual(req.params.sort, "baz asc")
        self.assertEqual(req.get_sort(), [('baz','asc')])
        
    def test_solr_request_set_query_fields(self):
        req = SearchRequest("foo")
        self.assertIsNone(req.params.qf)
        req.set_query_fields("bar baz^1.2")
        self.assertEqual(req.params.qf, "bar baz^1.2")
    
    def test_solr_request_add_sort(self):
        req = SearchRequest("foo")
        self.assertEqual(req.params.sort, None)
        req.add_sort("bar", "desc")
        self.assertEqual(req.params.sort, "bar desc")
        req.add_sort("baz", "asc")
        self.assertEqual(req.params.sort, "bar desc,baz asc")
        
    def test_solr_request_add_facet(self):
        req = SearchRequest("foo")   
        self.assertFalse(req.facets_on())
        self.assertNotIn('facet', req.params)
        req.add_facet('author')
        self.assertTrue(req.facets_on())
        self.assertEqual(req.get_facets(), [('author', None, None, None, None)])
        self.assertEqual(req.params['facet'], 'true')
        self.assertEqual(req.params['facet.field'], ['author'])
        req.add_facet('bibstem')
        self.assertEqual(req.get_facets(), [('author', None, None, None, None), ('bibstem', None, None, None, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem'])
        req.add_facet('keyword', 10)
        self.assertEqual(req.get_facets(), [('author', None, None, None, None), ('bibstem', None, None, None, None), ('keyword', 10, None, None, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem', 'keyword'])
        self.assertIn('f.keyword.facet.limit', req.params)
        self.assertEqual(req.params['f.keyword.facet.limit'], 10)
        req.add_facet('author', 10, 5)
        self.assertEqual(req.get_facets(), [('author', 10, 5, None, None), ('bibstem', None, None, None, None), ('keyword', 10, None, None, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem', 'keyword'])
        self.assertIn('f.author.facet.limit', req.params)
        self.assertIn('f.author.facet.mincount', req.params)
        self.assertEqual(req.params['f.author.facet.limit'], 10)
        self.assertEqual(req.params['f.author.facet.mincount'], 5)
        
    def test_solr_request_add_facet_output_key(self):
        
        req = SearchRequest("foo")
        req.add_facet("author", output_key="authorz")
        self.assertEqual(req.params['facet.field'], ["{!ex=dt key=authorz}author"])
        
        req = SearchRequest("foo")
        req.add_facet("title", limit=10, output_key="titlez")
        self.assertEqual(req.params['facet.field'], ["{!ex=dt key=titlez}title"])
        self.assertEqual(req.params['f.title.facet.limit'], 10)
        
    def test_solr_request_add_filter_query(self):
        req = SearchRequest("foo")   
        req.add_filter_query("bibstem:ApJ")
        self.assertEqual(req.params.fq, ['bibstem:ApJ'])
        req.add_filter_query("author:Kurtz,M")
        self.assertEqual(req.params.fq, ['bibstem:ApJ', 'author:Kurtz,M'])
        self.assertEqual(req.get_filter_queries(), ['bibstem:ApJ', 'author:Kurtz,M'])
        
    def test_solr_request_add_highlight(self):
        req = SearchRequest("foo")
        self.assertNotIn('hl', req.params)
        self.assertFalse(req.highlights_on())
        req.add_highlight("abstract")
        self.assertTrue(req.highlights_on())
        self.assertEqual(req.params['hl'], 'true')
        self.assertEqual(req.params['hl.fl'], 'abstract')
        self.assertEqual(req.get_highlights(), [('abstract', None, None)])
        req.add_highlight("full")
        self.assertEqual(req.params['hl.fl'], 'abstract,full')
        self.assertEqual(req.get_highlights(), [('abstract', None, None), ('full', None, None)])
        req.add_highlight('full', 2)
        self.assertEqual(req.get_highlights(), [('abstract', None, None), ('full', 2, None)])
        req.add_highlight('foo')
        req.add_highlight('bar')
        self.assertEqual(req.params['hl.fl'], 'abstract,full,foo,bar')
        req.add_highlight('baz', 3)
        req.add_highlight('fez', 3)
        self.assertEqual(req.params['f.baz.hl.snippets'], 3)
        self.assertEqual(req.params['f.fez.hl.snippets'], 3)
        self.assertNotIn('f.baz.hl.fragsize', req.params)
        req.add_highlight("blah", 3, 5000)
        self.assertEqual(req.params['f.blah.hl.fragsize'], 5000)
    
    def test_solr_request_add_facet_prefix(self):
        req = SearchRequest("foo")
        req.add_facet_prefix("author", "bar")
        self.assertIn("f.author.facet.prefix", req.params)
        self.assertEqual(req.params['f.author.facet.prefix'], "bar")        

#     def test_search_signal(self):
#         from adsabs.core.solr import signals
#         fixture = self.useFixture(SolrRawQueryFixture())
#         
#         @signals.search_signal.connect
#         def catch_search(request, **kwargs):
#             self._signal_test = request.q
#             
#         self.get_resp(solr.SolrRequest("foo"))
#         self.assertEqual(self._signal_test, "foo") 
#         
#     def test_error_signal(self):
#         from adsabs.core.solr import signals
#         
#         def reset_config(url, timeout):
#             config.SOLR_URL = url
#             config.SOLR_TIMEOUT = timeout
#         self.addCleanup(reset_config, config.SOLR_URL, config.SOLR_TIMEOUT)
#         config.SOLR_TIMEOUT = 1
#         config.SOLR_URL = 'http://httpbin.org/delay/3?' # see http://httpbin.org
#         
#         @signals.error_signal.connect
#         def catch_error(request, **kwargs):
#             self._signal_error = kwargs['error_msg']
#             
#         try:
#             self.get_resp(solr.SolrRequest("foo"))
#         except:
#             pass
#         self.assertTrue(hasattr(self, '_signal_error'))
#         self.assertTrue(self._signal_error.startswith("Something blew up"))

if __name__ == '__main__':
    unittest.main()
