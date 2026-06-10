# contents of conftest.py
from functools import wraps
from http.client import HTTPException
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError

import pytest
import requests
import urllib3

NETWORK_EXCEPTIONS = (
    requests.RequestException,
    urllib3.exceptions.HTTPError,
    HTTPException,
    HTTPError,
    URLError,
    TimeoutError,
    SocketTimeout,
)


def is_wrapped_network_failure(exc):
    return str(exc).startswith("FTP download failed:")


def skip_on_network_failure(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NETWORK_EXCEPTIONS as exc:
            pytest.skip(f"Skipping due to network failure: {exc}")
        except Exception as exc:
            if is_wrapped_network_failure(exc):
                pytest.skip(f"Skipping due to network failure: {exc}")
            raise

    return wrapper


# Test fixtures will be added here as needed for SRAweb and GEOweb tests
