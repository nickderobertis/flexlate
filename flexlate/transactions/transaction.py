import uuid
from enum import Enum
from pathlib import Path
from typing import Optional, List, Sequence

from git import Repo, Commit  # type: ignore
from pydantic import BaseModel, Field, UUID4, validator

from flexlate.exc import (
    CannotParseCommitMessageFlexlateTransaction,
    LastCommitWasNotByFlexlateException,
    TransactionMismatchBetweenBranchesException,
    InvalidNumberOfTransactionsException,
    TooFewTransactionsException,
    ExpectedMergeCommitException,
    CannotFindCorrectMergeParentException,
    UserChangesWouldHaveBeenDeletedException,
    MergeCommitIsNotMergingAFlexlateTransactionException,
    CannotFindMergeForTransactionException,
)
from flexlate.ext_git import (
    reset_current_branch_to_commit,
    get_commits_between_two_commits,
)
from flexlate.template_data import TemplateData

FLEXLATE_TRANSACTION_COMMIT_DIVIDER = (
    "\n\n-------------------BEGIN FLEXLATE TRANSACTION-------------------\n"
)


class TransactionType(str, Enum):
    ADD_SOURCE = "add source"
    ADD_OUTPUT = "add output"
    ADD_SOURCE_AND_OUTPUT = "add source and output"
    REMOVE_SOURCE = "remove source"
    REMOVE_OUTPUT = "remove output"
    UPDATE = "update"
    SYNC = "sync"


class FlexlateTransaction(BaseModel):
    type: TransactionType
    target: Optional[str] = None
    out_root: Optional[Path] = None
    data: Optional[Sequence[TemplateData]] = None
    id: UUID4 = Field(default_factory=lambda: uuid.uuid4())

    @validator("data", pre=True)
    def cast_data_into_sequence(cls, v):
        if isinstance(v, dict):
            return [v]
        return v

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


def reset_last_transaction(
    repo: Repo,
    transaction: FlexlateTransaction,
    merged_branch_name: str,
    template_branch_name: str,
):
    last_transaction = find_last_transaction_from_commit(
        repo.commit(), merged_branch_name, template_branch_name
    )
    if last_transaction.id != transaction.id:
        raise TransactionMismatchBetweenBranchesException(
            f"Found mismatching transaction ids: {last_transaction.id} and {transaction.id}"
        )
    earliest_commit = find_earliest_commit_that_was_part_of_transaction(
        repo, last_transaction, merged_branch_name, template_branch_name
    )

    is_template_branch = repo.active_branch.name == template_branch_name
    if is_template_branch:
        # On template branch, the only commits are flexlate transactions.
        # Therefore can just get the parent to find the commit before the
        # transaction started
        before_transaction_commit = _get_parent_commit(earliest_commit)
    else:
        # On output/user branch, typically the only commits are merging flexlate transactions
        # and user changes. So find the commit that merged this transaction,
        # then use its parent.
        try:
            merge_commit = find_earliest_merge_commit_for_transaction(
                repo, transaction, merged_branch_name, template_branch_name
            )
        except CannotFindMergeForTransactionException:
            # This is likely because the user has not made any changes in the repo yet,
            # and so the merges from the template branch are always fast-forwards.
            # In this case, it is a mirror of the template branch and so we should use
            # that logic
            before_transaction_commit = _get_parent_commit(earliest_commit)
        else:
            before_transaction_commit = (
                _get_non_flexlate_transaction_parent_from_flexlate_merge_commit(
                    merge_commit, merged_branch_name, template_branch_name
                )
            )

    assert_that_all_commits_between_two_are_flexlate_transactions_or_merges(
        repo,
        before_transaction_commit,
        repo.commit(),
        merged_branch_name,
        template_branch_name,
    )
    reset_current_branch_to_commit(repo, before_transaction_commit)


def find_last_transaction_from_commit(
    commit: Commit, merged_branch_name: str, template_branch_name: str
) -> FlexlateTransaction:
    if _is_flexlate_merge_commit(commit, merged_branch_name, template_branch_name):
        parent = _get_flexlate_transaction_parent_from_flexlate_merge_commit(
            commit, merged_branch_name, template_branch_name
        )
        return find_last_transaction_from_commit(
            parent, merged_branch_name, template_branch_name
        )
    return FlexlateTransaction.parse_commit_message(commit.message)


def find_earliest_merge_commit_for_transaction(
    repo: Repo,
    transaction: FlexlateTransaction,
    merged_branch_name: str,
    template_branch_name: str,
) -> Commit:
    # Walk back through commit tree, searching for the appropriate commit
    return _search_commit_tree_for_earliest_merge_commit_for_transaction(
        repo.commit(), transaction, merged_branch_name, template_branch_name
    )


def _search_commit_tree_for_earliest_merge_commit_for_transaction(
    commit: Commit,
    transaction: FlexlateTransaction,
    merged_branch_name: str,
    template_branch_name: str,
):
    # TODO: Better strategy for finding earliest merge commit for transaction
    #  The current strategy requires searching until the beginning of history.
    #  Add early stopping when hitting a user commit or different flexlate transaction
    search_commits = [commit]
    found_commits: List[Commit] = []
    # Breadth-first search
    while len(search_commits) > 0:
        this_commit = search_commits.pop(0)
        if _is_flexlate_merge_commit(
            this_commit, merged_branch_name, template_branch_name
        ):
            merge_transaction = _get_transaction_underlying_merge_commit(this_commit)
            if transaction.id == merge_transaction.id:
                found_commits.append(this_commit)
        search_commits.extend(list(this_commit.parents))

    if len(found_commits) == 0:
        raise CannotFindMergeForTransactionException(
            f"Could not find the merge commit for transaction {transaction}"
        )

    # Since BFS was used, last found commit should be the earliest
    return found_commits[-1]


def _get_transaction_underlying_merge_commit(commit: Commit) -> FlexlateTransaction:
    for parent in commit.parents:
        try:
            return FlexlateTransaction.parse_commit_message(parent.message)
        except CannotParseCommitMessageFlexlateTransaction:
            continue
    raise MergeCommitIsNotMergingAFlexlateTransactionException(
        f"Commit {commit.hexsha}: {commit.message}"
    )


def assert_last_commit_was_in_a_flexlate_transaction(
    repo: Repo, merged_branch_name: str, template_branch_name: str
):
    last_commit = repo.commit()
    if _is_flexlate_merge_commit(last_commit, merged_branch_name, template_branch_name):
        return
    if isinstance(last_commit.message, bytes):
        raise LastCommitWasNotByFlexlateException(
            f"Last commit was not made by flexlate, message is bytes"
        )
    try:

        FlexlateTransaction.parse_commit_message(last_commit.message)
    except CannotParseCommitMessageFlexlateTransaction as e:
        raise LastCommitWasNotByFlexlateException(
            f"Last commit was not made by flexlate: {last_commit.message}"
        ) from e


def assert_has_at_least_n_transactions(
    repo: Repo, n: int, merged_branch_name: str, template_branch_name: str
):
    if n < 0:
        raise InvalidNumberOfTransactionsException(
            "Number of transactions must be positive"
        )
    assert_last_commit_was_in_a_flexlate_transaction(
        repo, merged_branch_name, template_branch_name
    )
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
        if _is_flexlate_merge_commit(
            last_commit, merged_branch_name, template_branch_name
        ):
            last_commit = _get_flexlate_transaction_parent_from_flexlate_merge_commit(
                last_commit, merged_branch_name, template_branch_name
            )
        if isinstance(last_commit.message, bytes):
            # Flexlate never commits with binary messages
            return too_few_transactions()
        try:
            transaction = FlexlateTransaction.parse_commit_message(last_commit.message)
        except CannotParseCommitMessageFlexlateTransaction:
            return too_few_transactions()
        earliest_commit = _return_commit_if_begin_of_transaction_else_get_parent(
            last_commit, transaction, merged_branch_name, template_branch_name
        )
        num_to_verify -= 1
        if num_to_verify <= 0:
            return
        try:
            last_commit = _get_parent_commit(earliest_commit)
        except (HitInitialCommit, HitMergeCommit):
            return too_few_transactions()


def assert_that_all_commits_between_two_are_flexlate_transactions_or_merges(
    repo: Repo,
    start: Commit,
    end: Commit,
    merged_branch_name: str,
    template_branch_name: str,
):
    between_commits = get_commits_between_two_commits(repo, start, end)
    for commit in between_commits:
        if _is_flexlate_merge_commit(commit, merged_branch_name, template_branch_name):
            continue
        try:
            FlexlateTransaction.parse_commit_message(commit.message)
        except CannotParseCommitMessageFlexlateTransaction:
            raise UserChangesWouldHaveBeenDeletedException(
                f"Commit {commit.hexsha}: {commit.message} would have been deleted "
                f"by the flexlate undo strategy. An extra check prevented it. "
                f"Please raise this as an issue on Github"
            )


def find_earliest_commit_that_was_part_of_transaction(
    repo: Repo,
    transaction: FlexlateTransaction,
    merged_branch_name: str,
    template_branch_name: str,
) -> Commit:
    return _return_commit_if_begin_of_transaction_else_get_parent(
        repo.commit(), transaction, merged_branch_name, template_branch_name
    )


def _return_commit_if_begin_of_transaction_else_get_parent(
    commit: Commit,
    transaction: FlexlateTransaction,
    merged_branch_name: str,
    template_branch_name: str,
) -> Commit:
    try:
        parent_commit = _get_parent_commit(commit)
    except HitInitialCommit:
        return commit
    except HitMergeCommit:
        parent_commit = _get_flexlate_transaction_parent_from_flexlate_merge_commit(
            commit, merged_branch_name, template_branch_name
        )
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
            parent_commit, transaction, merged_branch_name, template_branch_name
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


def _get_flexlate_transaction_parent_from_flexlate_merge_commit(
    commit: Commit, merged_branch_name: str, template_branch_name: str
) -> Commit:
    if not _is_flexlate_merge_commit(commit, merged_branch_name, template_branch_name):
        raise ExpectedMergeCommitException("not a flexlate merge commit")
    if len(commit.parents) != 2:
        raise ExpectedMergeCommitException(f"has {len(commit.parents)} parents, not 2")
    flexlate_transaction_parents: List[Commit] = []
    for parent in commit.parents:
        try:
            FlexlateTransaction.parse_commit_message(parent.message)
            flexlate_transaction_parents.append(parent)
        except CannotParseCommitMessageFlexlateTransaction:
            pass
    if len(flexlate_transaction_parents) != 1:
        raise CannotFindCorrectMergeParentException(
            f"Cannot determine which of these commits is the flexlate transaction parent {flexlate_transaction_parents}"
        )
    return flexlate_transaction_parents[0]


def _get_non_flexlate_transaction_parent_from_flexlate_merge_commit(
    commit: Commit, merged_branch_name: str, template_branch_name: str
) -> Commit:
    if not _is_flexlate_merge_commit(commit, merged_branch_name, template_branch_name):
        raise ExpectedMergeCommitException("not a flexlate merge commit")
    if len(commit.parents) != 2:
        raise ExpectedMergeCommitException(f"has {len(commit.parents)} parents, not 2")
    non_flexlate_transaction_parents: List[Commit] = []
    for parent in commit.parents:
        try:
            FlexlateTransaction.parse_commit_message(parent.message)
        except CannotParseCommitMessageFlexlateTransaction:
            non_flexlate_transaction_parents.append(parent)
    if len(non_flexlate_transaction_parents) != 1:
        raise CannotFindCorrectMergeParentException(
            f"Cannot determine which of these commits is the non-flexlate transaction parent {non_flexlate_transaction_parents}"
        )
    return non_flexlate_transaction_parents[0]


def _is_flexlate_merge_commit(
    commit: Commit, merged_branch_name: str, template_branch_name: str
) -> bool:
    return (
        commit.message
        == f"Merge branch '{template_branch_name}' into {merged_branch_name}\n"
    )
