import ethel
from ethel.ethel import HOSTS


def test_ethel(mocker):
    """Should pass hostnames to initialize_apis."""
    mocked_initialize_apis = mocker.patch.object(ethel.ethel, "initialize_apis")
    ethel.Ethel("HOSTNAME_A", "HOSTNAME_B")
    mocked_initialize_apis.assert_called_once_with("HOSTNAME_A", "HOSTNAME_B")


def test_stage(mocker):
    """Should create an instance pointing to Stage environment."""
    mocked_initialize_apis = mocker.patch.object(ethel.ethel, "initialize_apis")
    e = ethel.Ethel.stage()
    mocked_initialize_apis.assert_called_once_with(*HOSTS["stage"])
    assert isinstance(e, ethel.Ethel)


def test_qa(mocker):
    """Should create an instance pointing to QA environment."""
    mocked_initialize_apis = mocker.patch.object(ethel.ethel, "initialize_apis")
    e = ethel.Ethel.qa()
    mocked_initialize_apis.assert_called_once_with(*HOSTS["qa"])
    assert isinstance(e, ethel.Ethel)


def test_create_account(mocker):
    """Should pass APIs to Account."""
    mocked_account = mocker.patch.object(ethel.ethel, "Account")
    e = ethel.Ethel("HOSTNAME_A", "HOSTNAME_B")
    e.create_account("USERNAME", "PASSWORD", accept_terms=False)
    mocked_account.assert_called_once_with(
        e.api, "USERNAME", "PASSWORD", accept_terms=False
    )
