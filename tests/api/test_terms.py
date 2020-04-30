import pytest

from ethel.api import TermsV1, EthelError


@pytest.fixture(scope="module")
def terms_v1(api_base: str) -> TermsV1:
    return TermsV1(api_base)


USER_NOT_FOUND = "com.redhat.services.termsv2.model.exceptions.UserNotFoundException"
TERMS_NOT_FOUND = (
    "com.redhat.services.termsv2.model.exceptions.NoActiveVerbiageForPdfIdException"
)


@pytest.mark.vcr()
def test_get_required_terms(terms_v1: TermsV1):
    """Fetch required terms."""
    terms = terms_v1.get_required_terms("username")
    assert len(terms) == 1


@pytest.mark.vcr()
def test_get_required_terms_nonexistent(terms_v1: TermsV1):
    """Should fail to fetch terms if user doesn't exist."""
    username = "this-username-doesnt-exist"
    with pytest.raises(EthelError) as e:
        terms_v1.get_required_terms(username)
    assert USER_NOT_FOUND in e.value.exception_type


@pytest.mark.vcr()
def test_get_all_terms(terms_v1: TermsV1):
    """Fetch required+optional terms."""
    terms = terms_v1.get_all_terms("username")
    assert len(terms) == 1


@pytest.mark.vcr()
def test_get_all_terms_nonexistent(terms_v1: TermsV1):
    """Should fail to fetch terms if user doesn't exist."""
    username = "this-username-doesnt-exist"
    with pytest.raises(EthelError) as e:
        terms_v1.get_all_terms(username)
    assert USER_NOT_FOUND in e.value.exception_type


@pytest.mark.vcr()
def test_accept_terms(terms_v1: TermsV1):
    """Should accept terms by id."""
    assert terms_v1.accept_terms("username", "05a33507-81a8-4a37-94e7-b37be33f87b9")


@pytest.mark.vcr()
def test_accept_terms_nonexistent_user(terms_v1: TermsV1):
    """Should fail to accept terms if user doesn't exist."""
    username = "this-username-doesnt-exist"
    with pytest.raises(EthelError) as e:
        terms_v1.accept_terms(username, "05a33507-81a8-4a37-94e7-b37be33f87b9")
    assert USER_NOT_FOUND in e.value.exception_type


@pytest.mark.vcr()
def test_accept_terms_nonexistent_pdfid(terms_v1: TermsV1):
    """Should fail to accept terms if terms id doesn't exist."""
    with pytest.raises(EthelError) as e:
        terms_v1.accept_terms("username", "this-is-not-an-id")
    assert TERMS_NOT_FOUND in e.value.exception_type
