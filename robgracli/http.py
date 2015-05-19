import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry


class HttpClient(object):
    '''
    A generic base class for HTTP clients, with connection pooling, sane
    timeouts and retries.

    :param connect_timeout: connection timeout, in seconds;
    :param read_timeout: read timeout, in seconds;
    :param max_retries:
        retry requests this number of time on network errors (only works for
        :meth:`get`);
    :param backoff_factor:
        factor used for exponential delays between retries;
    :param extra_requests_opts:
        additionnal keyworkd arguments passed to each
        :meth:`requests.Session.request` calls.
    '''

    def __init__(self, connect_timeout=5, read_timeout=2.5, max_retries=3,
            backoff_factor=1, **extra_requests_opts):
        self.timeout = (connect_timeout, read_timeout)
        self.extra_requests_opts = extra_requests_opts
        self.session = requests.Session()
        self.session.mount('http://', get_adapter(max_retries, backoff_factor))
        self.session.mount('https://', get_adapter(max_retries, backoff_factor))

    def request(self, method, url, data=None, params=None,
            raise_for_status=True):
        response = self.session.request(method, url, data=data, params=params,
                timeout=self.timeout, **self.extra_requests_opts)
        if raise_for_status:
            response.raise_for_status()
        return response

    def get(self, url, params=None, raise_for_status=True):
        return self.request('GET', url, data=None, params=params,
                raise_for_status=raise_for_status)

    def post(self, url, data=None, params=None, raise_for_status=True):
        return self.request('POST', url, data=data, params=params,
                raise_for_status=raise_for_status)


def get_adapter(max_retries, backoff_factor):
    retry = Retry(max_retries, backoff_factor=backoff_factor)
    return HTTPAdapter(max_retries=retry)
