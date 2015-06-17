from urlparse import urljoin
import datetime

from .http import HttpClient
from .exceptions import InvalidDataFormat, EmptyData


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
    :param metrics_prefix: a string prefixed to all metrics.

    Additional arguments are passed to :class:`robgracli.http.HttpClient`.
    '''

    def __init__(self, endpoint, min_queries_range=60 * 10, metrics_prefix='',
            *args, **kwargs):
        super(GraphiteClient, self).__init__(*args, **kwargs)
        self.endpoint = endpoint
        self.min_queries_range = min_queries_range
        self.metrics_prefix = metrics_prefix

    def get_metric_value(self, target, from_=60, aggregator=average):
        '''
        Get the current value of a metric, by aggregating Graphite datapoints
        over an interval.

        Values returned by *target* over the period *from_* are aggregated
        using the *aggregator* function, *from_* being in seconds from the most
        recent data point.

        Returns the resulting floating point value, or raise an
        :class:`~robgracli.exceptions.InvalidDataFormat` if the retured data is
        invalid, or :class:`~robgracli.exceptions.EmptyData` if there are no
        datapoints to aggregate (this can happen if there are only null data
        points in the returned data, or if :attr:`min_queries_range` is not
        large enough).
        '''
        target = self.metrics_prefix + target

        query_from = max(self.min_queries_range, from_)
        url = urljoin(self.endpoint, '/render')
        response = self.get(url, params={
            'target': target,
            'format': 'json',
            'from': '-%ss' % query_from,
        })
        data = response.json()

        # Check data format
        err_prefix = 'got invalid data for "%s": ' % target
        if not isinstance(data, list):
            raise InvalidDataFormat(err_prefix +
                    'expected a list but got a %s instead' % type(data))
        if not len(data):
            err_message = err_prefix + 'empty data returned'
            raise InvalidDataFormat(err_message)
        if len(data) > 1:
            err_message = err_prefix + 'multiple metrics returned'
            raise InvalidDataFormat(err_message)
        if not isinstance(data[0], dict):
            raise InvalidDataFormat(err_prefix + 'expected a dict '
                    'at item 0 but got a %s instead' % type(data[0]))

        # Filter data, removing null points and trimming to the desired range
        values = filter_values(data[0]['datapoints'], from_)
        if not values:
            raise EmptyData('got no valid data points for "%s"' % target)

        # Aggregate values
        return aggregator(values)


def filter_values(datapoints, max_age):
    '''
    Filter and extract values from raw Graphite *datapoints*.

    Keeps non-null values and with a maximum delta of *max_age* seconds from
    the most recent data point.
    '''
    # Convert timestamps and filter out null values
    datapoints = [(e[0], datetime.datetime.fromtimestamp(e[1]))
        for e in datapoints if e[0] is not None]
    if not len(datapoints):
        return []
    last_point_date = datapoints[-1][1]
    datapoints = filter(
        lambda (_, date): (last_point_date - date).total_seconds() <= max_age,
        datapoints)
    return [e[0] for e in datapoints]

