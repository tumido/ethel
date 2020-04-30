from datetime import date, timedelta

from .base import CERT, APIBase
from .exceptions import raises_from_ebs as raises_ethel_exception
from .utils import Template


class RegnumV5(APIBase):
    PAYLOAD_TEMPLATE = Template("payloads/pool.yml")

    def __init__(self, api_host: str) -> None:
        """Subscription registration API

        Access the API for creating subscription pools.

        Args:
            api_host (str): Base API host
        """
        super().__init__(f"https://subscription.{api_host}/svcrest/regnum/v5", cert=CERT)

    @raises_ethel_exception
    def order(
        self,
        username: str,
        sku_id: str,
        quantity: int,
        start_date: date,
        duration: timedelta,
    ) -> dict:
        """Request a subscription pool to be created.

        Args:
            username (str): Account's username.
            sku_id (str): Subscription SKU identifier.
            quantity (int): Pool quantity.
            start_date (date): Date when the pool should become active.
            duration (timedelta): How long the pool should last.

        Returns:
            dict: Information about the placed order.
        """
        payload = self.PAYLOAD_TEMPLATE.render(
            username=username,
            sku_id=sku_id,
            quantity=quantity,
            start_date=start_date,
            duration=duration.days,
        )

        response = self.api.put("/hock/order", json=payload)
        response.raise_for_status()
        return response.json()


class ActivationV2(APIBase):
    def __init__(self, api_host: str) -> None:
        """Subscription activation API

        Access the API for activating subscription pools in a organization.

        Args:
            api_host (str): Base API host
        """
        super().__init__(
            f"https://subscription.{api_host}/svcrest/activation/v2", cert=CERT
        )

    @raises_ethel_exception
    def activate(self, username: str, org_id: int, regnum: int, start_date: date) -> dict:
        """Activate a pool by a registration number.

        Args:
            username (str): Account's username (pool owner).
            org_id (int): Organization ID (pool owner).
            regnum (int): Registration number from the order system.
            start_date (date): Data when the pool should be activated.

        Returns:
            dict: Activation details.
        """
        params = dict(
            activationKey=regnum,
            startDate=str(start_date),
            systemName="genie",
            userName=username,
            vendor="REDHAT",
            webCustomerId=org_id,
        )

        response = self.api.post("/activate", json=params)
        response.raise_for_status()
        return response.json()
