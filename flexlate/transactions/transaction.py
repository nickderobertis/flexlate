import uuid
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, UUID4

from flexlate.exc import CannotParseCommitMessageFlexlateTransaction
from flexlate.template_data import TemplateData

FLEXLATE_TRANSACTION_COMMIT_DIVIDER = (
    "\n\n-------------------BEGIN FLEXLATE TRANSACTION-------------------\n"
)


class TransactionType(str, Enum):
    ADD_SOURCE = "add source"
    ADD_OUTPUT = "add output"
    REMOVE_SOURCE = "remove source"
    REMOVE_OUTPUT = "remove output"
    UPDATE = "update"


class FlexlateTransaction(BaseModel):
    type: TransactionType
    target: Optional[str] = None
    out_root: Optional[Path] = None
    data: Optional[TemplateData] = None
    id: UUID4 = Field(default_factory=lambda: uuid.uuid4())

    @classmethod
    def parse_commit_message(cls, message: str) -> "FlexlateTransaction":
        parts = message.split(FLEXLATE_TRANSACTION_COMMIT_DIVIDER)
        if len(parts) != 2:
            raise CannotParseCommitMessageFlexlateTransaction(
                f"Could not parse commit message {message}. After splitting "
                f"on the divider, got {len(parts)} parts instead of 2"
            )
        _, transaction_part = parts
        return cls.parse_raw(transaction_part)

    @property
    def commit_message(self) -> str:
        return self.json(indent=2)


def create_transaction_commit_message(
    commit_message: str, transaction: FlexlateTransaction
) -> str:
    return (
        commit_message
        + FLEXLATE_TRANSACTION_COMMIT_DIVIDER
        + transaction.commit_message
    )
