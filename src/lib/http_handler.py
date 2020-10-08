import requests, urllib
import json
from requests_aws4auth import AWS4Auth
import logging

SERVICE = "execute-api"


def authed(f):
    def do_auth(self, *args, **kwargs):
        if self._access_key is not None:
            self._auth = self._get_auth()

        return f(self, *args, **kwargs)

    return do_auth


class HttpHelper:
    _host = None
    _region = None
    _access_key = None
    _secret_key = None
    _session_token = None
    _auth = None
    _logger = None
    _default_headers = {
        "content-type": "application/json"
    }

    def __init__(self, host, stage, region, access_key, secret_key, session_token, custom_domain: bool = False,
                 logger: logging.Logger = None):
        self._host = host
        self._region = region
        self._stage = stage
        self._access_key = access_key
        self._secret_key = secret_key
        self._session_token = session_token
        self._custom_domain = custom_domain

        if logger is not None:
            self._logger = logger
        else:
            logging.basicConfig()
            self._logger = logging.getLogger("HttpHandler")
            self._logger.setLevel(logging.INFO)

    def get_base_path(self):
        base = self._host
        if self._stage is not None and self._custom_domain is False:
            base = f"{base}/{self._stage}"

        return base

    def _get_auth(self):
        return AWS4Auth(self._access_key, self._secret_key, self._region, SERVICE, session_token=self._session_token)

    def _get_url(self, data_type: str, path: str, query_params: str = None):
        if data_type is not None:
            full_path = f"{data_type}/{path}"
        else:
            full_path = f"{path}"

        encoded_path = urllib.parse.quote(full_path)

        if query_params is not None and len(query_params) > 0:
            encoded_path += f"?{urllib.parse.urlencode(query_params)}"

        return encoded_path

    def _make_path(self, encoded_path):
        path = f"{self.get_base_path()}/{encoded_path}"
        self._logger.debug(path)

        return path

    @authed
    def head(self, data_type: str, path: str, query_params: str = None):
        encoded_path = self._get_url(data_type, path, query_params)

        return requests.head(url=f"{self._make_path(encoded_path)}", auth=self._auth,
                             headers=self._default_headers)

    @authed
    def get(self, data_type: str, path: str, query_params: dict = None):
        encoded_path = self._get_url(data_type, path, query_params)

        return requests.get(url=self._make_path(encoded_path), auth=self._auth, headers=self._default_headers)

    @authed
    def put(self, data_type: str, path: str, path_params: str = None, put_body=None):
        encoded_path = self._get_url(data_type, path, path_params)

        return requests.put(url=f"{self._make_path(encoded_path)}", data=json.dumps(put_body), auth=self._auth,
                            headers=self._default_headers)

    @authed
    def post(self, data_type: str, path: str, query_params: str = None, post_body: dict = None):
        encoded_path = self._get_url(data_type, path, query_params)

        return requests.post(url=f"{self._make_path(encoded_path)}", data=json.dumps(post_body), auth=self._auth,
                             headers=self._default_headers)

    @authed
    def delete(self, data_type: str, path: str, delete_params: str = None, delete_body: dict = None):
        encoded_path = self._get_url(data_type, path, delete_params)

        return requests.delete(url=f"{self._make_path(encoded_path)}", data=json.dumps(delete_body),
                               auth=self._auth,
                               headers=self._default_headers)
