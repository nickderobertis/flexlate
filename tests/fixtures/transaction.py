from uuid import UUID

import pytest

from flexlate.transactions.transaction import FlexlateTransaction, TransactionType

ADD_SOURCE_ID = UUID("93f984ca-6e8f-45e9-b9b0-aebebfe798c1")
ADD_OUTPUT_ID = UUID("86465f4d-9752-4ae5-aaa7-791b4c814e8d")
ADD_SOURCE_AND_OUTPUT_ID = UUID("bf4cd42c-10b1-4bf9-a15f-294f5be738b0")
REMOVE_SOURCE_ID = UUID("c034ec63-d2b5-4d8c-aef1-f96e29a6f5d1")
REMOVE_OUTPUT_ID = UUID("79715a11-a3c4-40b1-a49b-9d8388e5c28d")
UPDATE_TRANSACTION_ID = UUID("347711b7-3bf9-484e-be52-df488f3cf598")
SYNC_TRANSACTION_ID = UUID("4825ce35-1a03-43de-ad8a-1ecc0ed68b62")


@pytest.fixture
def add_source_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.ADD_SOURCE, id=ADD_SOURCE_ID)


@pytest.fixture
def add_output_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.ADD_OUTPUT, id=ADD_OUTPUT_ID)


@pytest.fixture
def add_source_and_output_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(
        type=TransactionType.ADD_SOURCE_AND_OUTPUT, id=ADD_SOURCE_AND_OUTPUT_ID
    )


@pytest.fixture
def remove_source_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.REMOVE_SOURCE, id=REMOVE_SOURCE_ID)


@pytest.fixture
def remove_output_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.REMOVE_OUTPUT, id=REMOVE_OUTPUT_ID)


@pytest.fixture
def update_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.UPDATE, id=UPDATE_TRANSACTION_ID)


@pytest.fixture
def sync_transaction() -> FlexlateTransaction:
    yield FlexlateTransaction(type=TransactionType.SYNC, id=SYNC_TRANSACTION_ID)
