class GraphiteException(Exception):
    '''
    Base class for all errors.
    '''

class InvalidDataFormat(GraphiteException):
    '''
    Raised by :meth:`robgracli.client.GraphiteClient.get_metric_value` when the
    data returned by Graphite doesn't have the expected format.
    '''

class EmptyData(GraphiteException):
    '''
    Raised by :meth:`robgracli.client.GraphiteClient.get_metric_value` when
    there are no valid data points to aggregate.
    '''

