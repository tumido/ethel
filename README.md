# Ethel

Ethel is a tool that allows you to manipulate with accounts in Stage, QA or any other environment, buy Subscriptions, activate them and do other chores.

## Instalation

```sh
pip install ethel
```

## Usage

### Prerequisites

Before you can use Ethel, you have to set up your environment accordingly:

```sh
# Required:
EBS_CERT_PUBLIC=<PATH_TO_EBS_SSL_CLIENT_CERTIFICATE>
EBS_CERT_KEY=<PATH_TO_EBS_SSL_CLIENT_CERTIFICATE_KEY>

# Optional:
CANDLEPIN_USERNAME=<CANDLEPIN_SUPERUSER_USERNAME>  # Defaults to "candlepin_admin"
CANDLEPIN_PASSWORD=<CANDLEPIN_SUPERUSER_PASSWORD>  # Defaults to "candlepin_admin"
```

### Basic usage

The most basic usecase is to simply create an account and subscribe it to a product.

```python
>>> from ethel import Ethel

>>> ethel = Ethel.stage()

>>> account = ethel.create_account('some_fancy_username', 'not_so_secret_password')

>>> account.subscribe('product_sku')
```

Ethel provides access to Stage and QA environments via `Ethel.stage()` and `Ethel.qa()` class methods.

### Advanced usage

Ethel, by default, processes everything for you when the account is being created. Also, if account with the same username already exists, Ethel verifies your credentials and returns you the already existant account entry.

When account is being created, Ethel ensures that it's Candlepins owners are created (forces Candlepin refresh) and accepts all required Terms and Conditions. To disable this behavior, you can pass `create_owners=False` and/or `accept_terms=False` when creating account and do it yourself later:

```python
>>> account = ethel.create_account(
... "some_fancy_username",
... "not_so_secret_password",
... first_name="Gretchen",
... last_name="SomeOldSurname",
... email="grandmas.dont.have@emails.com",
... create_owners=False,
... accept_terms=False,
... )

>>> account.start_refresh()

>>> account.get_refresh_status()
'RUNNING'

>>> account.get_refresh_status()
'FINISHED'

>>> account.accept_all_terms(optional=True)  # Accepts also the optional Terms and Conditions
```

You can also specify more details about your desired subscription when asking Ethel to subscribe it you your account:

```python
>>> account.subscribe(
... 'product_sku',
... quantity=42,
... start_date='yesterday',  # accepts 'yesterday', 'today', 'tomorrow', ISO date 'YYYY-MM-DD' or datetime.date
... duration=365 # accepts integer that means 'days' or datetime.timedelta
... )
```

### Errors and Exceptions

If an exception is returned to Ethel from either Candlepin or the EBS rest API services, they are unified and interfaced as an `EthelError`. Depending on the exact API that raised the exception, the level of detail varies. Following properties are stored:

- `message` - Should contain the reason why the exception occurred.
- `message_type` - Class of the exception reason description (different to `exception_type`).
- `exception_type` - Type of exception (class name).
- `status_code` - HTTP status code (EBS likes to return HTTP_500 for any reason).
- `source` - API that caused the exception.
- `uuid` - Exception's tracking code for Candlepin API.
- `raw_error` - `HTTPError` object providing access to `PreparedRequest` and `Response` directly.

Ethel does not handle `requests.ConnectionError` and `requests.Timeout`. **For convenience a shorthand `EthelConnectionError` is provided.** Ethel doesn't retry any request, it's up to user to handle this behavior.

```python
>>> account = ethel.create_account('USERNAME', 'WRONG_PASSWORD')
EthelError: From: Candlepin(api_base_url=<CANDLEPIN_URL_FOR_THIS_ENV>). Reason: Invalid user credentials. Status code: 401. Call(method=GET, url=<CANDLEPIN_URL_FOR_THIS_ENV>)/users/<USERNAME>/owners).

>>> try:
...     account = ethel.create_account('<USERNAME>', '<WRONG_PASSWORD>')
... except EthelError as e:
...     logging.error("Status Code %d, Message: %s, Tracking code %s" % (e.status_code, e.message, e.uuid))

ERROR:root:Status Code 401, Message: Invalid user credentials, Tracking code e7275480-2c59-42fa-a6db-b8df6a9dc323
```

### Additional properties

Ethel stores few important properties for each of your accounts that might be usefull to you:

- Organization ID
- Candlepin Owner ID
- List of all Subscription orders done in this session
- List of all Activation orders done in this session

```python
>>> account.org_id
123456789

>>> account.owner_id
987654321

>>> account.orders
[...]

>>> account.activations
[...]
```

### View Account

And since Ethel allows you to have a Black Friday for subscriptions everyday, you may want to look up all the things you've bought:

```python
>>> account.list_pools()  # You can pass future=True argument to list also pools valid in future
[
    {
        'pool_id': '<USE_THIS_TO_SUBSCRIBE>',
        'sku_id': '<PRODUCT_SKU_ID>',
        'product_name': 'Fancy Product Name',
        'start_date': '2020-02-07T05:00:00+0000',
        'end_date': '2021-02-07T04:59:59+0000',
        'muiltiplier': None,
        'quantity': 'unlimited',
        'instance_multiplier': None
    },
    {
        'pool_id': '<ALSO_USE_THIS_TO_SUBSCRIBE>',
        'sku_id': '<ANOTHER_PRODUCT_SKU_ID>',
        'product_name': 'Fancy Product Name',
        'start_date': '2020-02-06T05:00:00+0000',
        'end_date': '2021-02-06T04:59:59+0000',
        'muiltiplier': None,
        'quantity': 1,
        'instance_multiplier': 16
    },
    ...
]
```

## Developer setup

After cloning this repo, setup the local environment via [Poetry](https://python-poetry.org/):

```sh
poetry install
```

### Prepared tasks

- `poetry run task lint` - runs [Mypy](http://mypy-lang.org/) and [Pylint](https://www.pylint.org/)
- `poetry run task test` - runs [Pytest](https://docs.pytest.org/en/latest/) test suite
