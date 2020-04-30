from datetime import date, datetime, timedelta
from typing import Any, Callable, Optional, Union


def parse_date(value: Union[datetime, date, str] = None) -> date:
    """Date mapping.

    Map to date from string, datetime or date.

    Examples:
    >>> parse_date('yesterday')
    datetime.date(2020, 2, 5)
    >>> parse_date('today')
    datetime.date(2020, 2, 6)
    >>> parse_date('tomorrow')
    datetime.date(2020, 2, 7)
    >>> parse_date('2020-02-08')
    datetime.date(2020, 2, 8)
    >>> parse_date(datetime.date(2020, 2, 9))
    datetime.date(2020, 2, 9)
    >>> parse_date(datetime.datetime(2020, 2, 10))
    datetime.date(2020, 2, 10)

    Args:
        value (Union[datetime, date, str], optional): Parsed value. Defaults to None.

    Returns:
        date: Targed date object.
    """
    # pylint: disable=too-many-return-statements

    if not value:
        return datetime.today().date()

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if value.lower() == "today":
        return date.today()

    if value.lower() == "yesterday":
        return date.today() - timedelta(days=1)

    if value.lower() == "tomorrow":
        return date.today() + timedelta(days=1)

    return date.fromisoformat(value)


def parse_duration(value: Union[int, timedelta] = timedelta(days=365)) -> timedelta:
    """Duration mapping.

    Parse a a timedelta or integer into a valid timedelta.

    Examples:
    >>> parse_duration()
    datetime.timedelta(days=365)
    >>> parse_duration(10)
    datetime.timedelta(days=10)
    >>> parse_duration(datetime.timedelta(days=10))
    datetime.timedelta(days=10)

    Args:
        value (Union[int, timedelta], optional): Parsed value. Defaults to a ~year.

    Raises:
        ValueError: Raised, if the duration is shorter than a day.

    Returns:
        timedelta: Target duration.
    """
    if isinstance(value, timedelta):
        if value < timedelta(days=1):
            raise ValueError("Duration must be at least a day")
        return value

    if not isinstance(value, int):
        raise ValueError("Supported datatype Union[int, timedata].")

    if value < 1:
        raise ValueError("Duration must be at least a day")
    return timedelta(days=value)


def apply_mapping(source_dict: dict, mapping: Union[Callable[[dict], Any], str]) -> Any:
    """Apply mapping to a dictionary.

    Apply a mapping function to a dictionary or query for a key directly.

    Args:
        source_dict (dict): Object of interest, where to look for data.
        mapping (Union[Callable[[dict], Any], str]): If string, it queries for the value
        in source_dict. If Callable, it calls this mapping function with source_dict as
        a argument.

    Returns:
        Any: Desired value.
    """
    if callable(mapping):
        return mapping(source_dict)
    return source_dict.get(mapping)


def get_instance_multiplier(source_dict: dict) -> Optional[int]:
    """Mapping function to get an instance multiplier.

    Args:
        source_dict (dict): Data source.

    Returns:
        int: Instance multiplier.
    """
    # "productAttributes" are encoded as {"name": ..., "value": ...} dicts
    # We're looking for value where x["name"] == "instance_multiplier"
    multiplier_gen = (
        int(a["value"])
        for a in source_dict.get("productAttributes", [])
        if a["name"] == "instance_multiplier"
    )

    return next(multiplier_gen, None)


def get_quantity(source_dict: dict) -> Union[float, str]:
    """Quantity mapping function.

    Args:
        source_dict (dict): Data source.

    Returns:
        Union[float, str]: Quantity.
    """
    quantity = source_dict["quantity"]
    if quantity < 0:
        return "unlimited"
    if quantity == 0:
        return 0

    instance_multiplier = get_instance_multiplier(source_dict) or 1

    return quantity / source_dict.get("multiplier", 1) / instance_multiplier
