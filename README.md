flask-solr-query
============

Flask extension for querying solr

Usage
-----

```python
from flask import Flask
from flask.ext.solr_query import FlaskSolrQuery 

app = Flask(__name__)
app.config['SOLR_URL'] = 'http://hostname:8983/solr/collection1/select'
solr = FlaskSolrQuery()
solr.init_app(app)

```
... then in your request contexts

```python

r = g.solr.query("foo OR bar")
```
Configuration
-------------

The following app.config settings are recognized:
* **SOLR_URL** (required)
* **SOLR_PERSISTENT** (default True)
* **SOLR_TIMEOUT** (defaults to python's socket._GLOBAL_DEFAULT_TIMEOUT)
* **SOLR_POST_HEADERS**
* **SOLR_MAX_RETRIES** (default 3)
* **SOLR_SSL_CRED**
* **SOLR_HTTP_BASIC_AUTH**

The **SOLR_HTTP_BASIC_AUTH** and **SOLR_SSL_CRED** values should be tuples containing
('http_auth','http_pass') and ('ssl_key','ssl_cert') respectively. 

All settings correspond to the constructor args to solrpy's SolrConnection 
class. See http://packages.python.org/solrpy/reference.html#connections for
more info.
