import json

import pytest
import mock
from httmock import all_requests, HTTMock

from ..client import GraphiteClient, filter_values
from ..exceptions import InvalidDataFormat, EmptyData


SINGLE_METRIC_DATA = [{
    'datapoints': [
        [524.9439252336449, 1417629030],
        [625.8536585365854, 1417629040],
        [581.9166666666666, 1417629050],
    ],
    'target': 'foo'
}]
MULTI_METRIC_DATA = [SINGLE_METRIC_DATA[0], SINGLE_METRIC_DATA[0]]
METRIC_WITH_NULL_DATA = [{
    'datapoints': [
        [524.9439252336449, 1417629030],
        [None, 1417629040],
        [581.9166666666666, 1417629050],
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


def build_json_response(data):
    @all_requests
    def json_response(url, request):
        return {
            'status_code': 200,
            'content': json.dumps(data)
        }
    return json_response


def test_data_format_check():
    client = GraphiteClient('https://graphite.com')

    # Invalid type response
    with HTTMock(build_json_response({})):
        with pytest.raises(InvalidDataFormat):
            client.get_metric_value('metric.path')

    # Empty response
    with HTTMock(build_json_response([])):
        with pytest.raises(InvalidDataFormat):
            client.get_metric_value('metric.path')

    # Response containing invalid data
    with HTTMock(build_json_response([[]])):
        with pytest.raises(InvalidDataFormat):
            client.get_metric_value('metric.path')

    # Multiple metrics
    with HTTMock(build_json_response(MULTI_METRIC_DATA)):
        with pytest.raises(InvalidDataFormat):
            client.get_metric_value('metric.path')

    # Metric with only nulls
    with HTTMock(build_json_response(METRIC_WITH_ONLY_NULLS_DATA)):
        with pytest.raises(EmptyData):
            client.get_metric_value('metric.path')

    # Empty metric
    with HTTMock(build_json_response([{'datapoints': [], 'target': 'foo'}])):
        with pytest.raises(EmptyData):
            client.get_metric_value('metric.path')


def test_aggregators():
    client = GraphiteClient('https://graphite.com')
    with HTTMock(build_json_response(SINGLE_METRIC_DATA)):
        assert client.get_metric_value('metric.path') == 577.5714168122989
        assert client.get_metric_value('metric.path', aggregator=max) == 625.8536585365854
        assert client.get_metric_value('metric.path', aggregator=min) == 524.9439252336449
    with HTTMock(build_json_response(METRIC_WITH_NULL_DATA)):
        assert client.get_metric_value('metric.path') == 553.4302959501558
        assert client.get_metric_value('metric.path', aggregator=max) == 581.9166666666666
        assert client.get_metric_value('metric.path', aggregator=min) == 524.9439252336449


def test_filter_values():
    ref_datapoints = SINGLE_METRIC_DATA[0]['datapoints']
    ref_values = [d[0] for d in ref_datapoints]
    # Test boundaries
    assert filter_values(ref_datapoints, 100) == ref_values
    assert filter_values(ref_datapoints, 10) == [ref_values[1], ref_values[2]]
    assert filter_values(ref_datapoints, 19) == [ref_values[1], ref_values[2]]
    assert filter_values(ref_datapoints, 20) == ref_values
    assert filter_values(ref_datapoints, 0) == [ref_values[-1]]
    # Nones are filtered out
    assert filter_values([[None, 1], [1, 2], [None, 3]], 100) == [1]


@mock.patch('robgracli.http.HttpClient.get', autospec=True)
def test_metrics_prefix(HttpClient_get):
    response = mock.Mock()
    response.json.return_value = SINGLE_METRIC_DATA
    HttpClient_get.return_value = response

    client = GraphiteClient('https://graphite.com', metrics_prefix='foo.')
    client.get_metric_value('bar')

    HttpClient_get.assert_called_once_with(client, mock.ANY, params={
        'target': 'foo.bar',
        'format': mock.ANY,
        'from': mock.ANY,
    })
