import os

from .base import APIBase
from .exceptions import raises_from_candlepin as raises_ethel_exception

ADMIN_AUTH = (
    os.getenv("CANDLEPIN_USERNAME", "candlepin_admin"),
    os.getenv("CANDLEPIN_PASSWORD", "candlepin_admin"),
)


class Candlepin(APIBase):
    def __init__(self, api_host: str) -> None:
        """Candlepin API

        Access the Candlepin API for subscription pool management.

        Args:
            api_host (str): Base API host
        """
        super().__init__(f"http://{api_host}/candlepin")

    def refresh(self, org_id: int) -> dict:
        """Force a Candlepin refresh.

        Forces Candlepin to synchronize EBS subscriptions to internal database.
        Requires admin access.

        Args:
            org_id (int): Organization ID of the user

        Returns:
            dict: Refresh job details
        """
        response = self.api.put(
            f"/owners/{org_id}/subscriptions",
            params=dict(auto_create_owner=True),
            auth=ADMIN_AUTH,
        )
        response.raise_for_status()
        return response.json()

    @raises_ethel_exception
    def get_job(self, job_id: str) -> dict:
        """Get job details.

        Args:
            job_id (str): Job ID

        Returns:
            dict: Job details
        """
        response = self.api.get(f"/jobs/{job_id}", auth=ADMIN_AUTH,)
        response.raise_for_status()
        return response.json()

    @raises_ethel_exception
    def get_owners(self, username: str, password: str) -> list:
        """Get list of owners.

        Args:
            username (str): Account's username.
            password (str): Account's password.

        Returns:
            list: List of account owners. Should contain 1 owner only.
        """
        response = self.api.get(f"/users/{username}/owners", auth=(username, password),)
        response.raise_for_status()
        return response.json()

    def delete_owner(self, username: str, password: str, owner_id: int) -> None:
        # pylint: disable=missing-function-docstring
        raise NotImplementedError

    @raises_ethel_exception
    def get_pools(
        self, username: str, password: str, owner_id: int, future: bool = False
    ) -> list:
        """Get list of subscription pools.

        Args:
            username (str): Account's username.
            password (str): Account's password.
            owner_id (int): Account's owner ID.
            future (bool, optional): List also subscription pools available in future.
                Defaults to False.

        Returns:
            list: List of pools available to the account.
        """
        response = self.api.get(
            f"/owners/{owner_id}/pools",
            params=dict(listall=True, add_future=future),
            auth=(username, password),
        )
        response.raise_for_status()
        return response.json()

    def delete_pool(self, username: str, password: str, pool_id: int) -> None:
        # pylint: disable=missing-function-docstring
        raise NotImplementedError

    def delete_user(self, username: str, password: str) -> None:
        # pylint: disable=missing-function-docstring
        raise NotImplementedError
