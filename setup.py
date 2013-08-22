"""
Flask-SolrQuery
-------------

Flask extension for querying solr
"""
from setuptools import setup

setup(
    name='Flask-SolrQuery',
    version='0.1',
    url='http://github.com/flask-solr-query',
    license='MIT',
    author='Jay Luker',
    author_email='jay.luker@gmail.com',
    description='A Flask extension for querying solr',
    long_description=__doc__,
    py_modules=['flask_solr_query'],
    install_requires=[
        'Flask',
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries'
        ],
)
