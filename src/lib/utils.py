import os
import boto3
from src.lib.credentials import Credentials


def get_credentials() -> Credentials:
    _access_key = None
    _secret_key = None
    _session_token = None

    # support boto3 based configuration of credentials
    session = boto3.session.Session()
    if session is not None:
        credentials = session.get_credentials().get_frozen_credentials()
        _access_key = credentials.access_key
        _secret_key = credentials.secret_key
        if session.get_credentials().token is not None:
            _session_token = session.get_credentials().token
    else:
        # attempt to get creds from environment
        _access_key = os.getenv("aws_access_key_id")
        _secret_key = os.getenv("aws_secret_access_key")
        _session_token = os.getenv("aws_session_token")

    credentials = Credentials(access_key=_access_key, secret_key=_secret_key, session_token=_session_token)

    return credentials


def resolve_url_info(url: str) -> tuple:
    url_tokens = url.split("/")

    if "http" in url:
        url_tokens = url_tokens[2:]

    if len(url_tokens) == 1:
        return url_tokens[0], None, True
    else:
        return url_tokens[0], url_tokens[1], False
