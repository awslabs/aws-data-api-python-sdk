import boto3
import json
import os
from src.lib.http_handler import HttpHelper
from datetime import datetime
import logging


class DataApiControlPlane:
    _base_uris = None
    _region_name = None
    _override_url = None
    _tls = True

    def __init__(self, region_name, override_url=None, tls=True):
        self._region_name = region_name
        self._override_url = override_url
        self._tls = tls

    def _load_uris(self):
        if self._base_uris is None:
            # load the base URI's from config
            file_dir = os.path.dirname(__file__)
            with open(f"{file_dir}/endpoints.json", 'r') as f:
                self._base_uris = json.load(f)

    def is_custom_domain(self, stage):
        stage_info = self._base_uris.get(stage)

        if stage_info.get('URL') is not None:
            return True
        else:
            return False

    def connect(self, from_url: str, access_key: str, secret_key: str, session_token: str = None,
                force_refresh: bool = False):
        _access_key = access_key
        _secret_key = secret_key
        _session_token = session_token

        # support boto3 based configuration of credentials if they aren't provided
        if access_key is None and secret_key is None:
            session = boto3.session.Session()
            credentials = session.get_credentials().get_frozen_credentials()
            _access_key = credentials.access_key
            _secret_key = credentials.secret_key
            if session.get_credentials().token is not None:
                _session_token = session.get_credentials().token

        file_dir = os.path.dirname(__file__)
        filepath = f"{file_dir}/endpoints.json"

        if not os.path.exists(filepath) or force_refresh:
            url_tokens = from_url.split("/")

            # create an http handler just for the bootstrap request
            http_handler = HttpHelper(host="/".join(url_tokens[:-1]), stage=url_tokens[len(url_tokens) - 1],
                                      region=self._region_name, access_key=_access_key,
                                      secret_key=_secret_key, session_token=_session_token)
            endpoints = http_handler.get(data_type=None, path="data-apis").json()

            if endpoints is not None and endpoints.get("message") is None:
                endpoints["RefreshDate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # write the endpoint config to endpoints.json.del
                with open(filepath, 'w+') as f:
                    json.dump(endpoints, f, sort_keys=True, indent=4)

                # refresh the default URL list
                self._load_uris()
            else:
                raise Exception(f"Unable to connect to Data API at {from_url} using supplied credentials")

    def _get_stage_addr(self, stage):
        if stage in self._base_uris:
            stage_info = self._base_uris.get(stage)

            if "URL" in stage_info:
                return stage_info.get('URL')
            else:
                return stage_info.get('Endpoint')
        else:
            return None

    def get_endpoint(self, stage):
        self._load_uris()
        stage_address = self._get_stage_addr(stage)
        uri = self._override_url if self._override_url is not None else stage_address
        proto = "https" if self._tls is True else "http"
        if self._override_url is None:
            return stage_address
        else:
            return f"{proto}://{self._override_url}"
