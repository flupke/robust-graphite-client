from urlparse import urljoin
from collections import OrderedDict

from .http import HttpClient


def average(values):
    return float(sum(values)) / len(values)


class GraphiteClient(HttpClient):
    '''
    A simple client for querying Graphite.

    :param endpoint: the Graphite URL;
    :param min_queries_range:
        The minimum range of data to query. Graphite occasionally returns empty
        data when querying small time ranges (probably on busy servers). The
        workaround is to query a larger time range and filter out unneeded
        values, e.g. if we want the data points from 1 minute ago, we query 10
        minutes and filter out the oldest 9 minutes.

        Care must be taken when choosing this value, if it's too large Graphite
        may return aggregated values, so it must be adapted to your storage
        schemas.

        As a guideline, the default value of 10 minutes gave good results on
        our server for querying 1 minute data ranges with a
        ``10s:1d,1min:7d,10min:1y`` retention schema;

    Additional arguments are passed to :class:`robgracli.http.HttpClient`.
    '''

    def __init__(self, endpoint, min_queries_range=60 * 10, *args, **kwargs):
        super(GraphiteClient, self).__init__(*args, **kwargs)
        self.endpoint = endpoint
        self.min_queries_range = min_queries_range

    def query(self, query, from_=60):
        '''
        Return datapoints for *query* over the last *from_* seconds.

        The return value is an :class:`~collections.OrderedDict` with target
        names as keys and datapoints ``(value, timestamp)`` pairs as values.
        '''
        query_from = max(self.min_queries_range, from_)
        url = urljoin(self.endpoint, '/render')
        response = self.get(url, params={
            'target': query,
            'format': 'json',
            'from': '-%ss' % query_from,
        })
        data = response.json()
        ret = OrderedDict()
        for entry in data:
            ret[entry['target']] = trim_datapoints(entry['datapoints'], from_)
        return ret

    def aggregate(self, query, from_=60, aggregator=average):
        '''
        Get the current value of a metric, by aggregating Graphite datapoints
        over an interval.

        Values returned by *query* over the last *from_* seconds are aggregated
        using the *aggregator* function, after filtering out None values.

        The return value is an :class:`~collections.OrderedDict` with target
        names as keys and aggregated values as values, or None for targets that
        returned no datapoints or only None values.
        '''
        data = self.query(query, from_)
        ret = OrderedDict()
        for key, values in data.items():
            values = [v[0] for v in values if v[0] is not None]
            if len(values):
                ret[key] = aggregator(values)
            else:
                ret[key] = None
        return ret


def trim_datapoints(datapoints, max_age):
    if len(datapoints):
        last_ts = datapoints[-1][1]
        return filter(lambda (_, ts): last_ts - ts <= max_age, datapoints)
    else:
        return []
