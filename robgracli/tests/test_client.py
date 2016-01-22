import json

import pytest

from ..exceptions import BadResponse
from ..client import GraphiteClient, trim_datapoints


SINGLE_METRIC_DATA = [{
    'datapoints': [
        [1., 1417629030],
        [2., 1417629040],
        [3., 1417629050],
    ],
    'target': 'foo'
}]
MULTI_METRIC_DATA = [
    {
        'datapoints': [
            [1., 1417629030],
            [2., 1417629040],
            [3., 1417629050],
        ],
        'target': 'foo'
    },
    {
        'datapoints': [
            [1., 1417629030],
            [2., 1417629040],
            [3., 1417629050],
        ],
        'target': 'bar'
    },
]
METRIC_WITH_NULL_DATA = [{
    'datapoints': [
        [1., 1417629030],
        [None, 1417629040],
        [2., 1417629050],
    ],
    'target': 'foo'
}]
METRIC_WITH_ONLY_NULLS_DATA = [{
    'datapoints': [
        [None, 1417629030],
        [None, 1417629040],
        [None, 1417629050],
    ],
    'target': 'foo'
}]


def test_query(httpserver):
    httpserver.serve_content(json.dumps(SINGLE_METRIC_DATA))
    client = GraphiteClient(httpserver.url)
    assert client.query('metric') == {
        'foo': SINGLE_METRIC_DATA[0]['datapoints'],
    }


def test_query_multi(httpserver):
    httpserver.serve_content(json.dumps(MULTI_METRIC_DATA))
    client = GraphiteClient(httpserver.url)
    assert client.query('metric') == {
        'foo': MULTI_METRIC_DATA[0]['datapoints'],
        'bar': MULTI_METRIC_DATA[1]['datapoints'],
    }


def test_aggregate(httpserver):
    httpserver.serve_content(json.dumps(SINGLE_METRIC_DATA))
    client = GraphiteClient(httpserver.url)
    assert client.aggregate('metric') == {'foo': 2.}
    assert client.aggregate('metric', aggregator=max) == {'foo': 3.}
    assert client.aggregate('metric', aggregator=min) == {'foo': 1.}


def test_aggregate_with_nulls(httpserver):
    httpserver.serve_content(json.dumps(METRIC_WITH_NULL_DATA))
    client = GraphiteClient(httpserver.url)
    assert client.aggregate('metric') == {'foo': 1.5}


def test_aggregate_with_only_nulls(httpserver):
    httpserver.serve_content(json.dumps(METRIC_WITH_ONLY_NULLS_DATA))
    client = GraphiteClient(httpserver.url)
    assert client.aggregate('metric') == {'foo': None}


def test_trim_datapoints_boundaries():
    dp = SINGLE_METRIC_DATA[0]['datapoints']
    assert trim_datapoints(dp, 100) == dp
    assert trim_datapoints(dp, 10) == [dp[1], dp[2]]
    assert trim_datapoints(dp, 19) == [dp[1], dp[2]]
    assert trim_datapoints(dp, 20) == dp
    assert trim_datapoints(dp, 0) == [dp[-1]]


def test_server_error(httpserver):
    error_body = 'internal error'
    httpserver.serve_content(error_body, code=500)
    client = GraphiteClient(httpserver.url)
    with pytest.raises(BadResponse) as exc:
        client.query('metric')
        assert error_body in exc.value
