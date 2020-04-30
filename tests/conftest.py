import os
import re
import pytest  # type: ignore
from ethel import Account
from ethel.api import API
from urllib.parse import urlsplit, urlunsplit


@pytest.fixture
def api(mocker) -> API:
    """Mocked API fixture."""
    return API(
        candlepin=mocker.patch("ethel.api.Candlepin", autospec=True),
        user=mocker.patch("ethel.api.UserV1", autospec=True),
        regnum=mocker.patch("ethel.api.RegnumV5", autospec=True),
        activation=mocker.patch("ethel.api.ActivationV2", autospec=True),
        terms=mocker.patch("ethel.api.TermsV1", autospec=True),
    )


@pytest.fixture
def account(api: API, mocker) -> Account:  # pylint: disable=redefined-outer-name
    """Account instance fixture."""
    new_account = Account(api, "USERNAME", "PASSWORD")
    new_account._owner_id = 1234  # pylint: disable=protected-access
    new_account._org_id = 5678  # pylint: disable=protected-access
    mocker.resetall()
    return new_account


@pytest.fixture(scope="module")
def vcr_config() -> dict:
    def scrub_hostname(request):
        request.uri = urlunsplit(urlsplit(request.uri)._replace(netloc="HOSTNAME.com"))
        return request

    def scrub_urls_from_response(response):
        response["body"]["string"] = re.sub(
            b'http.*?(?=")',
            b"http://HOSTNAME.com/some_url",
            response["body"]["string"],
        )
        return response

    return dict(
        before_record_request=scrub_hostname,
        before_record_response=scrub_urls_from_response,
        filter_headers=[("authorization", None)],
        match_on=["uri", "method", "raw_body"],
    )


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    # Put all cassettes in tests/cassettes/{module}/{test_case}.yaml
    return os.path.join("tests/cassettes", request.module.__name__)


@pytest.fixture(scope="session")
def api_base() -> str:
    """Use QA host for API requests cassette recording"""
    return "qa.api.redhat.com"
