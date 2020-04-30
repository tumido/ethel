from .account import Account
from .api import initialize_apis

HOSTS = dict(
    stage=("stage.api.redhat.com", "candlepin.dist.stage.ext.phx2.redhat.com"),
    qa=("qa.api.redhat.com", "candlepin.corp.qa.redhat.com"),
)


class Ethel:
    def __init__(self, rest_host: str, candlepin_host: str):
        """Ethel.

        Args:
            candlepin_host (str): Host of targed Candlepin
            rest_host (str): Base host for all REST APIs
        """
        self.api = initialize_apis(rest_host, candlepin_host)

    @classmethod
    def stage(cls) -> "Ethel":
        """Returns Ethel instance for Stage environment."""
        return cls(*HOSTS["stage"])

    @classmethod
    def qa(cls) -> "Ethel":  # pylint: disable=invalid-name
        """Returns Ethel instance for QA environment."""
        return cls(*HOSTS["qa"])

    def create_account(self, *args, **kwargs) -> Account:
        """Creates a new account.

        New account is created if it doesn't exist. If it does, it tries to
        log in into the account.

        Returns:
            Account: Account object.
        """
        return Account(self.api, *args, **kwargs)
