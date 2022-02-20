from git import Repo

from flexlate.branch_update import undo_transaction_in_flexlate_branches
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import assert_repo_is_in_clean_state
from flexlate.styles import console, styled, INFO_STYLE, print_styled, SUCCESS_STYLE
from flexlate.transactions.transaction import (
    assert_last_commit_was_in_a_flexlate_transaction,
    FlexlateTransaction,
    reset_last_transaction,
    assert_has_at_least_n_transactions,
    find_last_transaction_from_commit,
)


class Undoer:
    def undo_transaction(
        self,
        repo: Repo,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        last_transaction = find_last_transaction_from_commit(
            repo.commit(), merged_branch_name, template_branch_name
        )

        # Reset the flexlate branches
        undo_transaction_in_flexlate_branches(
            repo,
            last_transaction,
            merged_branch_name=merged_branch_name,
            base_merged_branch_name=base_merged_branch_name,
            template_branch_name=template_branch_name,
            base_template_branch_name=base_template_branch_name,
        )

        # Reset the user's branch
        reset_last_transaction(
            repo, last_transaction, merged_branch_name, template_branch_name
        )

    def undo_transactions(
        self,
        repo: Repo,
        num_transactions: int = 1,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    ):
        assert_repo_is_in_clean_state(repo)
        assert_last_commit_was_in_a_flexlate_transaction(
            repo, merged_branch_name, template_branch_name
        )
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")
        # Fail fast if there are too few transactions
        assert_has_at_least_n_transactions(
            repo, num_transactions, merged_branch_name, template_branch_name
        )

        with console.status(
            styled(f"Undoing {num_transactions} flexlate transactions", INFO_STYLE)
        ):
            for i in range(num_transactions):
                print_styled(f"Undoing transaction {i + 1}", INFO_STYLE)
                self.undo_transaction(
                    repo,
                    merged_branch_name=merged_branch_name,
                    base_merged_branch_name=base_merged_branch_name,
                    template_branch_name=template_branch_name,
                    base_template_branch_name=base_template_branch_name,
                )
                print_styled(
                    f"Successfully reversed transaction {i + 1}", SUCCESS_STYLE
                )
