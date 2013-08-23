
Flask extension for querying solr

Initialization
-----

Initialization follows the typical flask extension model.

```python
from flask import Flask
from flask.ext.solrquery import FlaskSolrQuery 

app = Flask(__name__)
app.config['SOLR_URL'] = 'http://hostname:8983/solr/collection1/select'
solr = FlaskSolrQuery(app)

```

View Usage
----------

```python

from flask.ext.solrquery import solr

resp = solr.query("black holes")
hits = resp.get_hits()

```

Response Callback
-----------------
Flask-SolrQuery provides a simple wrapper class, SearchResponseMixin, to represent the data returned by solr. You can do nothing and this class will be used by default. Otherwise you can customize how the response is respresented by registering a response loader callback function that utilizes your own response class (which could be a subclass of the included SearchResponseMixin class).

```python
@solr.response_callback
def my_response_loader(data, **kwargs):
    return MySearchResponse(data, **kwargs)
```
 
Configuration
-------------

The following app.config settings are recognized:
* **SOLR_URL** (required)
* **SOLR_KEEPALIVE** (default True)
* **SOLR_TIMEOUT** (defaults to python's socket._GLOBAL_DEFAULT_TIMEOUT)
