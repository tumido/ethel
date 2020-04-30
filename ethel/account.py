from datetime import date, datetime, timedelta
from typing import List, Union

from .api import API
from .utils import (apply_mapping, get_instance_multiplier, get_quantity,
                    parse_date, parse_duration)


class Account:
    def __init__(
        self,
        api: API,
        username: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        create_owners: bool = True,
        accept_terms: bool = True,
    ) -> None:
        """
        New account.

        Create new account.

        Args:
            api (API): API data structure instance.
            username (str): Username to use for the new account.
            password (str): Password to use for the new account.
            first_name (str, optional): Specify the first name. Defaults to None.
            last_name (str, optional): Specify the last name. Defaults to None.
            email (str, optional): Specify the email. Defaults to None.
            create_owners (bool, optional): Perform a Candlepin refresh to populate
                candlepin owners account. Defaults to True.
            accept_terms (bool, optional): Activate the account by acception Terms and
                Conditions. Defaults to True.
        """
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.api = api

        self._org_id: int = None  # type: ignore
        self._owner_id: int = None  # type: ignore
        self._latest_refresh_job_id: str = None  # type: ignore
        self.orders: List[dict] = []
        self.activations: List[dict] = []

        if self.does_exist():
            self.login()
            return

        self.create()

        if create_owners:
            self.start_refresh()

        if accept_terms:
            self.accept_all_terms()

    @property
    def org_id(self) -> int:
        """Organization ID.

        Get the account's organization ID if not cached already.

        Returns:
            int: Organization ID
        """
        if self._org_id is None:
            account_list = self.api.user.login(self.username)
            account = account_list[0] if account_list else {}
            self._org_id = account.get("orgId")

        return self._org_id

    @property
    def owner_id(self) -> int:
        """Candlepin owner account ID.

        Get the Candlepin Owner account ID if not cached already.

        Returns:
            int: Owner ID
        """
        if not self._owner_id:
            owners = self.api.candlepin.get_owners(self.username, self.password)
            if not len(owners) == 1:
                raise IndexError('A single owner is expected', owners)
            self._owner_id = int(owners[0].get("key"))

        return self._owner_id

    def does_exist(self) -> bool:
        """Check if account already exists.

        Check if there's only one account with the same username

        Returns:
            bool: True if the account exists
        """
        return len(self.api.user.login(self.username)) == 1

    def create(self) -> bool:
        """Create the user account via API request.

        Returns:
            bool: True if account is created successfully
        """
        account_id = self.api.user.create(
            username=self.username,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
        )
        return isinstance(account_id, int)

    def login(self) -> bool:
        """Login to Candlepin using own credentials.

        Raises:
            EthelError: In case credentials are not valid.

        Returns:
            bool: True if everything is OK.
        """
        self.api.candlepin.get_owners(self.username, self.password)
        return True

    POOL_ATTRIBUTES_MAPPING = dict(
        pool_id="id",
        sku_id="productId",
        product_name="productName",
        start_date="startDate",
        end_date="endDate",
        muiltiplier="multiplier",
        quantity=get_quantity,
        instance_multiplier=get_instance_multiplier,
    )

    def list_pools(  # pylint: disable=dangerous-default-value
        self, future: bool = False, filter_attributes: dict = POOL_ATTRIBUTES_MAPPING
    ) -> list:
        """List all subscriptions to this account.

        Args:
            future (bool, optional): List also subscription pools available in future.
                Defaults to False.
            filter_attributes (dict, optional): This parameter allows you to modify what
                values are parsed out of the API response. If set to empty dict, it
                returns raw API respose, as is. Supported format:
                    key: Target attribute name
                    value: Either a key of the API response dict or a callable
                Defaults to Account.POOL_ATTRIBUTES_MAPPING

        Returns:
            list: List of all subscriptions.
        """
        raw_pools = self.api.candlepin.get_pools(
            self.username, self.password, self.owner_id, future=future
        )
        if not filter_attributes:
            return raw_pools

        pools = [
            {k: apply_mapping(pool, v) for k, v in filter_attributes.items()}
            for pool in raw_pools
        ]

        return pools

    def start_refresh(self) -> None:
        """Requests a Candlepin refresh job.

        Requests Candlepin to propagate EBS changes to it's internal database, making
        new users and new subscriptions available.
        """
        job_id = self.api.candlepin.refresh(self.org_id).get("id")
        if job_id:
            self._latest_refresh_job_id = job_id

    def get_refresh_status(self) -> str:
        """Check refresh job status.

        If a refresh job was previously started, this method allows to query
        Candlepin for it's current state.

        Returns:
            str: Job status
        """
        if not self._latest_refresh_job_id:
            return "UNKNOWN"

        job = self.api.candlepin.get_job(self._latest_refresh_job_id)
        return job.get("state", "UNKNOWN")

    def subscribe(
        self,
        sku_id: str,
        quantity: int = 1,
        start_date: Union[datetime, date, str] = None,
        duration: Union[timedelta, int] = 365,
    ) -> int:
        """Create subscription to a product.

        Order a SKU and activate the subscription pool, so it's ready to be consumed.
        Subscription availability timeframe can be adjusted by modifying a start_date
        and duration. However, APIs consider duration in days only. Also not many
        subscriptions are available to be created with a duration set to just few days.
        Therefore, it's advised, if you want to create a subscription that lasts just
        for a few days, rather antidate the start_date.

        Args:
            sku_id (str): SKU identifier.
            quantity (int, optional): SKU quantity. Defaults to 1.
            start_date (Union[datetime, date, str], optional): Start date of the
                subscription. See ethel.utils.parse_date for all accepted values.
                Defaults to None.
            duration (Union[timedelta, int], optional): Subscription duration. See
                ethel.utils.parse_duration for all accepted values. Defaults to 365.

        Returns:
            int: Subscription ID
        """
        start_date = parse_date(start_date)
        duration = parse_duration(duration)

        order = self.api.regnum.order(
            self.username, sku_id, quantity, start_date, duration
        )
        self.orders.append(order)
        registration_num = order["regNumbers"][0][0]["regNumber"]

        activation = self.api.activation.activate(
            self.username, self.org_id, registration_num, start_date
        )
        self.activations.append(activation)
        return activation["id"]

    def accept_all_terms(self, optional: bool = False) -> None:
        """Accept all Terms and Conditions.

        Lists and accepts all required (and optional) Terms and Conditions.

        Args:
            optional (bool): Accept also optional Terms. Dafaluts to False
        """
        if optional:
            all_terms = self.api.terms.get_all_terms(self.username)
        else:
            all_terms = self.api.terms.get_required_terms(self.username)

        # Accept terms using a randomly selected PDF translation
        for terms in all_terms:
            translations = terms.get("translations", [])
            if len(translations) <= 0:
                continue

            pdf_id = translations[0].get("termsPdfId")
            self.api.terms.accept_terms(self.username, pdf_id)
