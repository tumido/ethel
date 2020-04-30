from datetime import date, datetime, timedelta

import hypothesis.strategies as st
import pytest  # type: ignore
from hypothesis import given

from ethel import utils


def test_parse_date_from_none():
    """Should parse date from date."""
    assert utils.parse_date() == date.today()


@given(st.dates())
def test_parse_date_from_date(given_date: date):
    """Should parse date from date."""
    assert utils.parse_date(given_date) == given_date


@given(st.dates())
def test_parse_date_from_date_str(given_date: date):
    """Should parse date from date as an ISO string."""
    assert utils.parse_date(given_date.isoformat()) == given_date


@given(st.datetimes())
def test_parse_date_from_datetime(given_datetime: datetime):
    """Should parse date from datetime."""
    assert utils.parse_date(given_datetime) == given_datetime.date()


@given(
    st.sampled_from([("yesterday", -1), ("today", 0), ("tomorrow", 1)])
    .map(lambda s: (s[0], date.today() + timedelta(days=s[1])))
    .flatmap(lambda s: st.sampled_from([(s[0].lower(), s[1]), (s[0].upper(), s[1])]))
)
def test_parse_date_from_str(given_date):
    """Should parse date from day string."""
    assert utils.parse_date(given_date[0]) == given_date[1]


def test_parse_duration_from_none():
    """Should parse duration from None."""
    assert utils.parse_duration() == timedelta(days=365)


def test_parse_duration_from_invalid():
    """Should parse duration from invalid type."""
    with pytest.raises(ValueError):
        utils.parse_duration("some text")


@given(st.integers(min_value=1, max_value=999999999))
def test_parse_duration_from_int_positive(days):
    """Should parse duration from int."""
    assert utils.parse_duration(days) == timedelta(days=days)


@given(st.integers(max_value=0))
def test_parse_duration_from_int_negative(days):
    """Should not parse duration from negative int."""
    with pytest.raises(ValueError):
        utils.parse_duration(days)


@given(st.timedeltas(min_value=timedelta(days=1)))
def test_parse_duration_from_delta_positive(days):
    """Should parse duration from timedelta."""
    assert utils.parse_duration(days) == days


@given(st.timedeltas(max_value=timedelta(hours=23)))
def test_parse_duration_from_delta_negative(days):
    """Should not parse duration from negative timedelta."""
    with pytest.raises(ValueError):
        utils.parse_duration(days)


@given(
    st.integers().map(
        lambda i: (
            i,
            {"productAttributes": [{"name": "instance_multiplier", "value": i}]},
        )
    )
)
def test_get_instance_multiplier_positive(source):
    """Should get instance multiplier from dict."""
    assert utils.get_instance_multiplier(source[1]) == source[0]


def test_get_instance_multiplier_negative():
    """Should not get instance multiplier if not present."""
    assert utils.get_instance_multiplier({"productAttributes": []}) is None


@given(
    st.sampled_from([("unlimited", -1), (0, 0)]).map(
        lambda i: (i[0], dict(quantity=i[1]))
    )
)
def test_get_quantity_edge_cases(source):
    """Should get unlimited or zero quantity."""
    assert utils.get_quantity(source[1]) == source[0]


@given(
    source=st.fixed_dictionaries(
        {"quantity": st.integers(min_value=1), "multiplier": st.integers(min_value=1)}
    ),
    instance_multiplier=st.integers(min_value=1),
)
def test_get_quantity(source, instance_multiplier, mocker):
    """Should calculate instance multiplier."""
    mocker.patch("ethel.utils.get_instance_multiplier", return_value=instance_multiplier)
    assert (
        utils.get_quantity(source)
        == source["quantity"] / source["multiplier"] / instance_multiplier
    )


@given(st.sampled_from(["key", lambda x: x["key"]]))
def test_apply_mapping(mapping):
    """Should apply key or function mapping."""
    assert utils.apply_mapping(dict(key="value"), mapping) == "value"
