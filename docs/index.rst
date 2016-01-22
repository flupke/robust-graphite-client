.. robust-graphite-client documentation master file, created by
   sphinx-quickstart on Tue May 19 13:36:21 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to robust-graphite-client's documentation!
==================================================

A simple graphite querying library with workarounds on some rare bugs.

Usage::

    import robgracli

    client = robgracli.GraphiteClient('http://my-graphite-server.com')
    client.aggregate('my.awesome.metric')

Reference:

.. toctree::
   :maxdepth: 2

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

