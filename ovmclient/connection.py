import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from six.moves.urllib import parse as urlparse

from ovmclient import exception

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Connection(object):
    def __init__(self, base_uri, username, password, verify_cert=False):
        session = requests.Session()
        session.auth = (username, password)
        session.verify = verify_cert
        session.headers.update({'Accept': 'application/json',
                                'Content-Type': 'application/json'})
        self._session = session
        self._base_uri = base_uri

    def _get_url(self, rel_path, params={}):
        url = "%s/%s" % (self._base_uri, rel_path)
        if params:
            query_str = urlparse.urlencode(params)
            url = "%s?%s" % (url, query_str)
        return url

    def _get_response_data(self, response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            try:
                data = response.json()
            except ValueError:
                data = response.text

            raise exception.OVMClientRequestException(
                data, response.status_code)
        except ValueError:
            return response.text

    def get(self, rel_path, params={}):
        return self._get_response_data(
            self._session.get(self._get_url(rel_path, params)))

    def post(self, rel_path, data, params={}):
        data_json = json.dumps(data)
        return self._get_response_data(
            self._session.post(self._get_url(rel_path, params), data_json))

    def put(self, rel_path, data, params={}):
        data_json = json.dumps(data)
        return self._get_response_data(
            self._session.put(self._get_url(rel_path, params), data_json))

    def delete(self, rel_path):
        return self._get_response_data(
            self._session.delete(self._get_url(rel_path)))
