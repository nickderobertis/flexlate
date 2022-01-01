import pytest

from flexlate.transactions.transaction import FlexlateTransaction, TransactionType


@pytest.fixture
def add_source_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.ADD_SOURCE)


@pytest.fixture
def add_output_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.ADD_OUTPUT)


@pytest.fixture
def remove_source_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.REMOVE_SOURCE)


@pytest.fixture
def remove_output_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.REMOVE_OUTPUT)


@pytest.fixture
def update_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.UPDATE)
