from datetime import timedelta, date

from hypothesis import given
import hypothesis.strategies as st
import pytest  # type: ignore
from requests import HTTPError

from ethel import Account, EthelError
from ethel.api import API
from ethel.utils import apply_mapping

import tests.strategies as custom_st

# pylint: disable=protected-access,pointless-statement


def test_account_already_exists(mocker, api: API):
    """Should not create account if it already exists."""
    mocker.patch.object(Account, "does_exist", return_value=True)
    login = mocker.patch.object(Account, "login")
    create = mocker.patch.object(Account, "create")

    Account(api, "USERNAME", "PASSWORD")

    login.assert_called_once()
    create.assert_not_called()


def test_account_create(mocker, api: API):
    """Should create account."""
    mocker.patch.object(Account, "does_exist", return_value=False)
    create = mocker.patch.object(Account, "create")

    Account(api, "USERNAME", "PASSWORD")
    create.assert_called_once()


def test_account_should_create_owners(mocker, api: API):
    """Should start a refresh on account create by default."""
    mocker.patch.object(Account, "does_exist", return_value=False)
    start_refresh = mocker.patch.object(Account, "start_refresh")

    Account(api, "USERNAME", "PASSWORD")
    start_refresh.assert_called_once()


def test_account_should_accept_terms(mocker, api: API):
    """Should accept all required terms on create by default."""
    mocker.patch.object(Account, "does_exist", return_value=False)
    accept_all_terms = mocker.patch.object(Account, "accept_all_terms")

    Account(api, "USERNAME", "PASSWORD")
    accept_all_terms.assert_called_once_with()


@given(
    first_name=st.sampled_from(["FIRST_NAME", None]),
    last_name=st.sampled_from(["LAST_NAME", None]),
    email=st.sampled_from(["name@example.com", None]),
)
def test_account_accepts_additional_params(
    mocker, api: API, first_name: str, last_name: str, email: str
):
    """Should create account with additional params, if requested."""
    mocker.patch.object(Account, "does_exist", return_value=False)
    start_refresh = mocker.patch.object(Account, "start_refresh")
    accept_all_terms = mocker.patch.object(Account, "accept_all_terms")

    Account(
        api,
        "USERNAME",
        "PASSWORD",
        first_name=first_name,
        last_name=last_name,
        email=email,
        create_owners=False,
        accept_terms=False,
    )

    api.user.create.assert_called_with(
        username="USERNAME",
        password="PASSWORD",
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    start_refresh.assert_not_called()
    accept_all_terms.assert_not_called()


def test_org_id(api: API):
    """Account's Organization ID property is fetched."""
    org_id = 123456
    api.user.login.return_value = [{"orgId": org_id}]
    account = Account(api, "USERNAME", "PASSWORD")

    assert account._org_id is None
    api.user.login.reset_mock()
    account.org_id
    assert account.org_id == org_id
    api.user.login.assert_called_once()


def test_owner_id(api: API):
    """Account's Owner ID property is fetched."""
    owner_id = 123456
    api.candlepin.get_owners.return_value = [{"key": owner_id}]
    account = Account(api, "USERNAME", "PASSWORD")

    assert account._owner_id is None
    account.owner_id
    assert account.owner_id == owner_id
    api.candlepin.get_owners.assert_called_once()


@given(st.lists(st.just({'key': 1234}), min_size=2) | st.just([]))
def test_no_owner_exception(api: API, owners: list):
    api.candlepin.get_owners.return_value = owners
    account = Account(api, "USERNAME", "PASSWORD")
    with pytest.raises(IndexError):
        account.owner_id


@given(st.just([]) | st.just([{"orgId": 123456}]))
def test_does_exist(account, api: API, accounts_found: list):
    """Should return bool if account exists."""
    api.user.login.return_value = accounts_found
    assert account.does_exist() == bool(accounts_found)


def test_create(api: API):
    """Account create should be truthy."""
    api.user.create.return_value = 123456
    account = Account(api, "USERNAME", "PASSWORD")
    api.user.create.assert_called_once()
    assert account.create()


def test_login_fails(api: API, account: Account):
    """If Candlepin raises error, login should fail."""
    api.candlepin.get_owners.side_effect = EthelError("msg", raw_error=HTTPError())
    with pytest.raises(EthelError):
        account.login()


def test_start_refresh(api: API, account: Account):
    """Should start refresh job track refresh ID."""
    api.candlepin.refresh.return_value = {"id": 123456}  # type: ignore
    account.start_refresh()
    api.candlepin.refresh.assert_called_once()  # type: ignore
    assert account._latest_refresh_job_id == 123456


def test_get_refresh_status_if_none(account: Account):
    """Should fail to check refresh job status if missing job ID."""
    account._latest_refresh_job_id = None  # type: ignore
    assert account.get_refresh_status() == "UNKNOWN"


def test_get_refresh_status(api: API, account: Account):
    """Should get job status for job ID"""
    account._latest_refresh_job_id = "123_job_id"
    api.candlepin.get_job.return_value = {"state": "FINISHED"}
    assert account.get_refresh_status() == "FINISHED"
    api.candlepin.get_job.assert_called_once_with("123_job_id")


@given(custom_st.terms)
def test_accept_all_terms_required(api, account, given_terms):
    """Should accept each of required terms once only."""
    api.terms.get_required_terms.return_value = given_terms
    api.terms.accept_terms.reset_mock()
    account.accept_all_terms()
    api.terms.get_required_terms.assert_called()
    api.terms.get_all_terms.assert_not_called()

    call_count = custom_st.count_terms(given_terms)
    assert api.terms.accept_terms.call_count == call_count


@given(custom_st.terms)
def test_accept_all_terms_optional(api, account, given_terms):
    """Should accept each of required+optional terms once only."""
    api.terms.get_all_terms.return_value = given_terms
    api.terms.accept_terms.reset_mock()
    account.accept_all_terms(optional=True)
    api.terms.get_required_terms.assert_not_called()
    api.terms.get_all_terms.assert_called()

    call_count = custom_st.count_terms(given_terms)
    assert api.terms.accept_terms.call_count == call_count


@given(custom_st.pools)
def test_list_pools(mocker, api: API, account: Account, raw_pools):
    """Should list pools with default mapping."""
    api.candlepin.get_pools.return_value = raw_pools

    apply_mapping_spy = mocker.patch(
        "ethel.account.apply_mapping", side_effect=apply_mapping
    )
    pools = account.list_pools()
    assert len(pools) == len(raw_pools)

    expected_call_count = len(account.POOL_ATTRIBUTES_MAPPING) * len(raw_pools)

    assert apply_mapping_spy.call_count == expected_call_count


@given(custom_st.pools)
def test_list_pools_no_filter(api: API, account: Account, raw_pools):
    """Should list raw pools without mapping."""
    api.candlepin.get_pools.return_value = raw_pools
    pools = account.list_pools(filter_attributes={})
    assert pools == raw_pools


@given(custom_st.pools)
def test_list_pools_custom_filter(api: API, account: Account, raw_pools):
    """Should list pools with custom mapping."""
    api.candlepin.get_pools.return_value = raw_pools
    pools = account.list_pools(filter_attributes={"my_id": "id"})
    assert pools == list(map(lambda p: {"my_id": p["id"]}, raw_pools))


def test_list_pools_future(api: API, account: Account):
    """Should list future pools."""
    api.candlepin.get_pools.return_value = []
    account.list_pools(future=True)
    api.candlepin.get_pools.assert_called_with("USERNAME", "PASSWORD", 1234, future=True)


@given(order=custom_st.order, sku_id=st.text(), activation=custom_st.activation)
def test_subscribe(mocker, api: API, account: Account, order, sku_id, activation):
    """Should subscribe to SKU with default settings."""
    api.regnum.order.return_value = order
    api.activation.activate.return_value = activation
    assert account.subscribe(sku_id) == activation["id"]
    api.regnum.order.assert_called_with(
        "USERNAME", sku_id, 1, date.today(), timedelta(days=365)
    )
    api.activation.activate.assert_called_with("USERNAME", 5678, mocker.ANY, date.today())
    assert order in account.orders
    assert activation in account.activations


@given(
    order=custom_st.order,
    sku_id=st.text(),
    activation=custom_st.activation,
    quantity=st.integers(min_value=1),
    duration=st.timedeltas(min_value=timedelta(days=1)),
    start_date=st.dates(),
)
def test_subscribe_optional_args(
    mocker,
    api: API,
    account: Account,
    order,
    sku_id,
    activation,
    quantity,
    duration,
    start_date,
):
    """Should subscribe to SKU with additional parameters."""
    api.regnum.order.return_value = order
    api.activation.activate.return_value = activation
    activation_id = account.subscribe(
        sku_id, quantity=quantity, start_date=start_date, duration=duration
    )
    assert activation_id == activation["id"]
    api.regnum.order.assert_called_with(
        "USERNAME", sku_id, quantity, start_date, duration
    )
    api.activation.activate.assert_called_with("USERNAME", 5678, mocker.ANY, start_date)
    assert order in account.orders
    assert activation in account.activations
