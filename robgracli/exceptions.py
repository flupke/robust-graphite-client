class GraphiteException(Exception):
    '''
    Base class for all errors.
    '''


class BadResponse(GraphiteException):
    '''
    Raised when the graphite server returns an error response.
    '''

    def __init__(self, response):
        self.response = response
        err = '''graphite returned an error (status={status}):
{sep}
Graphite response
{sep}
{response}
{sep}'''.format(status=response.status_code,
                sep='-' * 79,
                response=response.text)
        super(BadResponse, self).__init__(err)
