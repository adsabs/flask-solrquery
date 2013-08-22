
Flask extension for querying solr

Usage
-----

```python
from flask import Flask
from flask.ext.solrquery import FlaskSolrQuery 

app = Flask(__name__)
app.config['SOLR_URL'] = 'http://hostname:8983/solr/collection1/select'
solr = FlaskSolrQuery(app)

```
... then in your views

```python

from flask.ext.solrquery import solr

resp = solr.query("black holes")
hits = resp.get_hits()

```
Configuration
-------------

The following app.config settings are recognized:
* **SOLR_URL** (required)
* **SOLR_KEEPALIVE** (default True)
* **SOLR_TIMEOUT** (defaults to python's socket._GLOBAL_DEFAULT_TIMEOUT)
