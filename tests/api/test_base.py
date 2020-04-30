import hypothesis.strategies as st
from hypothesis import given

from ethel.api.base import APIBase, APISession


@given(st.sampled_from(["get", "options", "head", "post", "put", "patch", "delete"]))
def test_api_session(mocker, method):
    """Should prepend base url to requests.Session.<method> call urls."""
    mocked_session = mocker.patch("ethel.api.base.super")
    mocker.patch.object(APISession, "close")
    session = APISession("https://example.com/some/path/")

    getattr(session, method)("/endpoint")
    getattr(mocked_session(), method).assert_called_once_with(
        "https://example.com/some/path/endpoint"
    )


@given(
    st.fixed_dictionaries(
        dict(), optional=dict(cert=st.just(("CERT", "KEY")), verify=st.booleans())
    )
)
def test_api_session_optional_params(params):
    """Should pass optional params to parent."""
    session = APISession("https://example.com/some/path/", **params)
    assert session.cert == params.get("cert")
    assert session.verify == params.get("verify", False)


def test_api_session_close_on_delete(mocker):
    """Should register a close handler in atexit."""
    register = mocker.patch("atexit.register")
    session = APISession("https://example.com/some/path/")
    register.assert_called_once_with(session.close)


def test_api_base_pass_to_session(mocker):
    """Should propagate base url to APISession."""
    mocked_session = mocker.patch("ethel.api.base.APISession")
    APIBase("https://example.com/some/path/")
    mocked_session.assert_called_once_with(
        "https://example.com/some/path/", mocker.ANY, mocker.ANY
    )


def test_api_base_repr():
    """Should use children classname in repr."""

    class SubAPI(APIBase):
        pass

    subapi = SubAPI("https://example.com/some/path/")
    assert repr(subapi) == "SubAPI(api_base_url=https://example.com/some/path)"
