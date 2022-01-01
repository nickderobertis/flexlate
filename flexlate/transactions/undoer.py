from git import Repo

from flexlate.branch_update import undo_transaction_in_flexlate_branches
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import assert_repo_is_in_clean_state
from flexlate.transactions.transaction import (
    assert_last_commit_was_in_a_flexlate_transaction,
    FlexlateTransaction,
    reset_last_transaction,
)


class Undoer:
    def undo_transaction(
        self,
        repo: Repo,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        assert_repo_is_in_clean_state(repo)
        assert_last_commit_was_in_a_flexlate_transaction(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")

        last_transaction = FlexlateTransaction.parse_commit_message(
            repo.commit().message
        )

        # Reset the flexlate branches
        undo_transaction_in_flexlate_branches(
            repo,
            last_transaction,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
        )

        # Reset the user's branch
        reset_last_transaction(repo, last_transaction)

    def undo_transactions(
        self,
        repo: Repo,
        num_transactions: int = 1,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        for _ in range(num_transactions):
            self.undo_transaction(
                repo,
                merged_branch_name=merged_branch_name,
                template_branch_name=template_branch_name,
            )
