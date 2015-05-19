import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry


class HttpClient(object):
    '''
    A generic base class for HTTP clients, with connection pooling, sane
    timeouts and retries.
    '''

    def __init__(self, connect_timeout=5, read_timeout=2.5, max_retries=3,
            backoff_factor=1):
        self.timeout = (connect_timeout, read_timeout)
        self.session = requests.Session()
        self.session.mount('http://', get_adapter(max_retries, backoff_factor))
        self.session.mount('https://', get_adapter(max_retries, backoff_factor))

    def request(self, method, url, data=None, params=None,
            raise_for_status=True):
        response = self.session.request(method, url, data=data, params=params,
                timeout=self.timeout)
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
