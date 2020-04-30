from functools import wraps

from requests import ConnectionError as RequestsConnectionError
from requests import HTTPError, Timeout

from .base import APIBase


class EthelError(IOError):
    def __init__(
        self,
        message: str,
        *args,
        raw_error: HTTPError,
        status_code: str = None,
        source: APIBase = None,
        exception_type: str = None,
        message_type: str = None,
        uuid: str = None,
    ):
        """Ethel Exception.

        Translation layer between raw HTTPError and it's payload.

        Args:
            message (str): Error message.
            raw_error (HTTPError): Raw requests.HTTPError object for further detail.
            status_code (str, optional): HTTP status code. Defaults to None.
            source (APIBase, optional): API which raised this exception.
                Defaults to None.
            exception_type (str, optional): Exception type as a string if available.
                Defaults to None.
            message_type (str, optional): Message type as a string if available.
                Defaults to None.
            uuid (str, optional): UUID of the operation if available. Defaults to None.
        """
        self.message = message
        self.status_code = status_code
        self.raw_error = raw_error
        self.source = source
        self.exception_type = exception_type
        self.message_type = message_type
        self.uuid = uuid

        super().__init__(*args)

    def __str__(self):
        status = f" Status code: {self.status_code}." if self.status_code else ""
        ex_type = f" Type: {self.exception_type}." if self.exception_type else ""

        request = self.raw_error.request
        call = f" Call(method={request.method}, url={request.url})."
        return f"From: {self.source}. Reason: {self.message}.{status}{ex_type}{call}"


class EthelConnectionError(RequestsConnectionError, Timeout):
    """Ethel's shorthand for easier catching of RequestsConnectionError and Timeout."""


def raises_from_candlepin(func):
    """Map Candlepin exception response JSON to EthelError.

    Args:
        func ([type]): Decorated function.

    Raises:
        EthelError

    Returns:
        Return value of func.
    """

    @wraps(func)
    def wrapper(self: APIBase, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HTTPError as http_error:
            try:
                response = http_error.response.json()
            except ValueError as value_error:
                raise EthelError(
                    message=str(value_error),
                    status_code=http_error.response.status_code,
                    exception_type="JSONDecodeError",
                    source=self,
                    raw_error=http_error,
                )

            raise EthelError(
                message=response["displayMessage"],
                status_code=http_error.response.status_code,
                source=self,
                uuid=response["requestUuid"],
                raw_error=http_error,
            )

    return wrapper


def raises_from_ebs(func):
    """Map EBS exception response JSON to EthelError.

    Args:
        func ([type]): Decorated function.

    Raises:
        EthelError

    Returns:
        Return value of func.
    """

    @wraps(func)
    def wrapper(self: APIBase, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HTTPError as http_error:
            try:
                response = http_error.response.json()
            except ValueError as value_error:
                # NOTE: EBS sometimes decides to rather return and empty response
                # pylint: disable=no-member
                message = (
                    "API returned an empty response"
                    if value_error.pos == 0  # type: ignore
                    else str(value_error)
                )

                raise EthelError(
                    message=message,
                    status_code=http_error.response.status_code,
                    exception_type="JSONDecodeError",
                    source=self,
                    raw_error=http_error,
                )

            raise EthelError(
                message=response["message"],
                message_type=response["msgName"],
                status_code=http_error.response.status_code,
                exception_type=response["type"],
                source=self,
                raw_error=http_error,
            )

    return wrapper
