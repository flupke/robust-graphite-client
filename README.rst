robust-graphite-client
======================

.. image:: https://readthedocs.org/projects/robust-graphite-client/badge/?version=latest
    :target: https://readthedocs.org/projects/robust-graphite-client/?badge=latest

.. image:: https://travis-ci.org/Stupeflix/robust-graphite-client.svg?branch=master
    :target: https://travis-ci.org/Stupeflix/robust-graphite-client

A simple graphite querying library with workarounds on some rare bugs

Usage
-----

.. code::

    import robgracli

    client = robgracli.GraphiteClient('http://my-graphite-server.com')
    result = client.aggregate('my.awesome.metric')
    print result['my.awesome.metric']

For details consult the `documentation <http://robust-graphite-client.readthedocs.org/>`_.

History
-------

1.0.0
~~~~~

Rewrote the client API to properly support queries returning multiple metrics.
``GraphiteClient`` now has two methods, ``query()`` to get raw data from
graphite and ``aggregate()`` to retrieve single values (e.g. the average of the
metrics over a period).

Both methods return ordered mappings, indexed by target.

0.1.0
~~~~~

Add *allow_multiple* argument to ``GraphiteClient.get_metric_value()``.

0.0.1 to 0.0.4
~~~~~~~~~~~~~~

First public releases, fixing bugs.
