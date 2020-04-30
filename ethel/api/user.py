from .base import CERT, APIBase
from .exceptions import raises_from_ebs as raises_ethel_exception
from .utils import Template


class UserV1(APIBase):
    CREATE_PAYLOAD_TEMPLATE = Template("payloads/user.yml")

    def __init__(self, api_host: str) -> None:
        """User API

        Access the old API for user management.

        Args:
            api_host (str): Base API host
        """
        super().__init__(f"https://user.{api_host}/svcrest/user/v3", cert=CERT)

    @raises_ethel_exception
    def create(
        self,
        username: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
    ) -> int:
        """Create user.

        Make a call to the /create endpoint with payload.

        Args:
            payload (dict): Json-like payload for the endpoint
            username (str): Acccount's username.
            password (str): Account's password.
            first_name (str, optional): First name, left blank if None.
            last_name (str, optional): Last name, left blank if None.
            email (str, optional): Account's email. Left blank if None.

        Returns:
            int: If successful, an account id is returned
        """
        payload = self.CREATE_PAYLOAD_TEMPLATE.render(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        response = self.api.post("/create", json=payload)
        response.raise_for_status()
        return response.json()

    @raises_ethel_exception
    def login(self, username: str) -> list:
        """Login user.

        Make a call to the /login endpoint with the nonstandard call.

        Args:
            username (str): Username used for the account

        Returns:
            list: List of users matching the username
        """
        response = self.api.get(f"/login={username}")
        response.raise_for_status()
        return response.json()


class UserV2(APIBase):
    CREATE_PAYLOAD_TEMPLATE = Template("payloads/user_v2.yml")

    def __init__(self, api_host: str) -> None:
        """User API

        Access the old API for user management.

        Args:
            api_host (str): Base API host
        """
        super().__init__(f"https://user.{api_host}/v2", cert=CERT)

    @raises_ethel_exception
    def create(
        self,
        username: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
    ) -> int:
        """Create user.

        Make a call to the /create endpoint with payload.

        Args:
            payload (dict): Json-like payload for the endpoint
            username (str): Acccount's username.
            password (str): Account's password.
            first_name (str, optional): First name, left blank if None.
            last_name (str, optional): Last name, left blank if None.
            email (str, optional): Account's email. Left blank if None.

        Returns:
            int: If successful, an account id is returned
        """
        payload = self.CREATE_PAYLOAD_TEMPLATE.render(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        response = self.api.post("/createUser", json=payload)
        response.raise_for_status()
        return response.json()

    @raises_ethel_exception
    def login(self, username: str) -> list:
        """Login user.

        Make a call to the /findUser endpoint with a payload searching for an exact
        match on username.

        Args:
            username (str): Username used for the account

        Returns:
            list: List of users matching the username
        """
        payload = dict(
            by=dict(authentication=dict(provider="Red Hat", principal=username))
        )
        response = self.api.post("/findUser", json=payload)
        response.raise_for_status()
        return response.json()
