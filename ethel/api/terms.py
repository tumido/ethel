from .base import CERT, APIBase
from .exceptions import raises_from_ebs as raises_ethel_exception


class TermsV1(APIBase):
    def __init__(self, api_host: str) -> None:
        """Terms API

        Access the API for Terms and Conditions management.

        Args:
            api_host (str): Base API host
        """
        super().__init__(
            f"https://terms.{api_host}/svcrest/terms/presentation", cert=CERT
        )

    @raises_ethel_exception
    def get_required_terms(self, username: str) -> list:
        """Get all Terms and Conditions the user is required to accept.

        Args:
            username (str): Account's username.

        Returns:
            list: List of events
        """
        params = dict(login=username, event="attachSubscription", site="candlepin")
        response = self.api.get("/required", params=params)
        response.raise_for_status()
        return response.json()

    @raises_ethel_exception
    def get_all_terms(self, username: str) -> list:
        """Get all Terms and Conditions for the user.

        List all, required as well as optional terms.

        Args:
            username (str): Account's username.

        Returns:
            list: List of events
        """
        params = dict(login=username, event="attachSubscription", site="candlepin")
        response = self.api.get("/available", params=params)
        response.raise_for_status()
        return response.json()

    @raises_ethel_exception
    def accept_terms(self, username: str, terms_id: int) -> bool:
        """Accept a Terms and Conditions document.

        Accepts single document based on its PDF ID.

        Args:
            username (str): Account's username.
            terms_id (int): PDF ID of the Terms and Conditions.

        Returns:
            bool: True if successfull
        """
        params = dict(
            login=username, pdfid=terms_id, acknowledgedcode="accepted", site="candlepin"
        )
        response = self.api.put("/ackterms", params=params)
        response.raise_for_status()
        return response.content == b""
