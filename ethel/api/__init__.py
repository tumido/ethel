"""Ethel's API module

Provides access to all APIs, that are used by Ethel.
"""

from dataclasses import dataclass

from .candlepin import Candlepin
from .exceptions import EthelConnectionError, EthelError
from .subscription import ActivationV2, RegnumV5
from .terms import TermsV1
from .user import UserV1


@dataclass
class API:
    candlepin: Candlepin
    user: UserV1
    regnum: RegnumV5
    activation: ActivationV2
    terms: TermsV1


def initialize_apis(rest_host: str, candlepin_host: str) -> API:
    """Initialize APIs.

    Populate a API namedtuple with API clients for desired endpoints.

    Args:
        candlepin_host (str): Host of targed Candlepin
        rest_host (str): Base host for all REST APIs

    Returns:
        API: namedtuple containing all the clients.
    """
    return API(
        candlepin=Candlepin(candlepin_host),
        user=UserV1(rest_host),
        regnum=RegnumV5(rest_host),
        activation=ActivationV2(rest_host),
        terms=TermsV1(rest_host),
    )


__all__ = ("API", "initialize_apis", "EthelError", "EthelConnectionError")
