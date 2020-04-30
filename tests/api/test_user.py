# pylint: disable=redefined-outer-name

import pytest  # type: ignore

from ethel.api import EthelError, UserV1


@pytest.fixture(scope="module")
def user_v1(api_base: str) -> UserV1:
    """Test Users V1 API fixture."""
    return UserV1(api_base)


@pytest.mark.vcr()
def test_create_new(user_v1: UserV1):
    """Create a new account."""
    account_id = user_v1.create("username", "PASSWORD")
    assert account_id == 12345678


@pytest.mark.vcr()
def test_create_new_propagate_optional(user_v1: UserV1):
    """Create a new account."""
    account_id = user_v1.create(
        "username",
        "PASSWORD",
        first_name="name",
        last_name="surname",
        email="name@surname.com",
    )
    assert account_id == 12345679


@pytest.mark.vcr()
def test_create_existent(user_v1: UserV1):
    """Should fail to create account that already exist."""
    user_v1.create("username", "PASSWORD")
    with pytest.raises(EthelError) as e:
        user_v1.create("username", "PASSWORD")
    assert "com.redhat.services.user.LoginExistsException" in e.value.exception_type
    assert "username" in e.value.message


@pytest.mark.vcr()
def test_login_exists(user_v1: UserV1):
    """Fetch account info for existing account."""
    account = user_v1.login("username")
    assert len(account) == 1
    assert account[0]["id"] == 12345678


@pytest.mark.vcr()
def test_login_fails(user_v1: UserV1):
    """Fetch nothing for nonexistant account."""
    account = user_v1.login("this-username-doesnt-exist")
    assert len(account) == 0
