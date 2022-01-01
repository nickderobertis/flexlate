import uuid
from enum import Enum
from pathlib import Path
from typing import Optional

from git import Repo, Commit
from pydantic import BaseModel, Field, UUID4

from flexlate.exc import (
    CannotParseCommitMessageFlexlateTransaction,
    LastCommitWasNotByFlexlateException,
    TransactionMismatchBetweenBranchesException,
    InvalidNumberOfTransactionsException,
    TooFewTransactionsException,
)
from flexlate.ext_git import reset_current_branch_to_commit
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


def reset_last_transaction(repo: Repo, transaction: FlexlateTransaction):
    last_transaction = FlexlateTransaction.parse_commit_message(repo.commit().message)
    if last_transaction.id != transaction.id:
        raise TransactionMismatchBetweenBranchesException(
            f"Found mismatching transaction ids: {last_transaction.id} and {transaction.id}"
        )
    earliest_commit = find_earliest_commit_that_was_part_of_transaction(
        repo, last_transaction
    )
    before_transaction_commit = _get_parent_commit(earliest_commit)
    reset_current_branch_to_commit(repo, before_transaction_commit)


def assert_last_commit_was_in_a_flexlate_transaction(repo: Repo):
    last_commit_message = repo.commit().message
    try:
        FlexlateTransaction.parse_commit_message(last_commit_message)
    except CannotParseCommitMessageFlexlateTransaction as e:
        raise LastCommitWasNotByFlexlateException(
            f"Last commit was not made by flexlate: {last_commit_message}"
        ) from e


def assert_has_at_least_n_transactions(repo: Repo, n: int):
    if n < 0:
        raise InvalidNumberOfTransactionsException(
            "Number of transactions must be positive"
        )
    assert_last_commit_was_in_a_flexlate_transaction(repo)
    if n == 1:
        return
    last_commit = repo.commit()
    num_to_verify = n

    def too_few_transactions():
        # Have hit the end but have not finished verifying, therefore there are too few transactions
        raise TooFewTransactionsException(
            f"Desired to undo {n} transactions but only found {n - num_to_verify}"
        )

    for _ in range(num_to_verify):
        try:
            transaction = FlexlateTransaction.parse_commit_message(last_commit.message)
        except CannotParseCommitMessageFlexlateTransaction:
            return too_few_transactions()
        earliest_commit = _return_commit_if_begin_of_transaction_else_get_parent(
            last_commit, transaction
        )
        num_to_verify -= 1
        if num_to_verify <= 0:
            return
        try:
            last_commit = _get_parent_commit(earliest_commit)
        except (HitInitialCommit, HitMergeCommit):
            return too_few_transactions()


def find_earliest_commit_that_was_part_of_transaction(
    repo: Repo, transaction: FlexlateTransaction
) -> Commit:
    return _return_commit_if_begin_of_transaction_else_get_parent(
        repo.commit(), transaction
    )


def _return_commit_if_begin_of_transaction_else_get_parent(
    commit: Commit, transaction: FlexlateTransaction
) -> Commit:
    try:
        parent_commit = _get_parent_commit(commit)
    except HitInitialCommit:
        return commit
    except HitMergeCommit:
        return commit
    try:
        commit_transaction = FlexlateTransaction.parse_commit_message(
            parent_commit.message
        )
    except CannotParseCommitMessageFlexlateTransaction:
        # Not a flexlate commit, so this must be the last in the transaction
        return commit

    if commit_transaction.id == transaction.id:
        # Parent is still in the same transaction. Recurse to find the original commit
        return _return_commit_if_begin_of_transaction_else_get_parent(
            parent_commit, transaction
        )

    # It is a flexlate commit, but different transaction. Therefore return this commit
    return commit


class HitInitialCommit(Exception):
    pass


class HitMergeCommit(Exception):
    pass


def _get_parent_commit(commit: Commit) -> Commit:
    parents = commit.parents
    if len(parents) == 0:
        raise HitInitialCommit
    if len(parents) > 1:
        raise HitMergeCommit
    return parents[0]
