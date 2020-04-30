import atexit
import os
from typing import Tuple

import requests

CERT = (os.getenv("EBS_CERT_PUBLIC", ""), os.getenv("EBS_CERT_KEY", ""))


class APISession(requests.Session):
    def __init__(
        self, api_base_url: str, cert: Tuple[str, str] = None, verify: bool = False,
    ) -> None:
        """API session with base url.

        A requests.Session with a base url and certificates settings available. It allows
        user to set a common host for all API requests to lower any confusion.

        Args:
            api_base_url (str): Base URL (API host)
            cert (tuple, optional): SSL client certificate to use for all requests.
                Defaults to None.
            verify (bool, optional): SSl CA verification mode. Defaults to False.
        """
        super().__init__()
        atexit.register(self.close)

        self.cert = cert
        self.verify = verify
        self.api_base_url = api_base_url.rstrip("/")

        # Inject api_base_url to the url param of every request.
        def override(parent_method):
            def wrapper(url, *args, **kwargs):
                return parent_method(self.api_base_url + url, *args, **kwargs)

            return wrapper

        parent = super()
        for method in ("get", "options", "head", "post", "put", "patch", "delete"):
            parent_method = getattr(parent, method)
            setattr(self, method, override(parent_method))


class APIBase:
    def __init__(
        self, api_base_url: str, cert: Tuple[str, str] = None, verify: bool = False
    ) -> None:
        """API Base.

        Args:
            api_base_url (str): Base API URL. Passed to APISession.
            cert (tuple, optional): SSL client certificate to use for all requests.
                Passed to APISession. Defaults to None.
            verify (bool, optional): SSl CA verification mode. Passed to APISession.
                Defaults to False.
        """
        self.api = APISession(api_base_url, cert, verify)

    def __repr__(self):
        return "{0}(api_base_url={1})".format(
            self.__class__.__name__, self.api.api_base_url
        )
