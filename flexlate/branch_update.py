import os
from pathlib import Path
from typing import Callable, Union, List

from git import Repo

from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import (
    temp_repo_that_pushes_to_branch,
    stage_and_commit_all,
    fast_forward_branch_without_checkout,
    checked_out_template_branch,
    merge_branch_into_current,
)
from flexlate.path_ops import make_func_that_creates_cwd_and_out_root_before_running
from flexlate.transactions.transaction import (
    FlexlateTransaction,
    reset_last_transaction,
)


def modify_files_via_branches_and_temp_repo(
    file_operation: Callable[[Path], None],
    repo: Repo,
    commit_message: str,
    out_root: Path,
    merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
    template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
):
    cwd = os.getcwd()
    current_branch = repo.active_branch

    make_dirs_add_operation = make_func_that_creates_cwd_and_out_root_before_running(
        out_root, file_operation
    )

    # Update the template only branch with the new template
    with temp_repo_that_pushes_to_branch(  # type: ignore
        repo, branch_name=template_branch_name
    ) as temp_repo:
        make_dirs_add_operation(Path(temp_repo.working_dir))  # type: ignore
        stage_and_commit_all(temp_repo, commit_message)

    # Bring the change into the merged branch
    # Update with changes from the main repo
    fast_forward_branch_without_checkout(repo, merged_branch_name, current_branch.name)
    with checked_out_template_branch(repo, branch_name=merged_branch_name):
        # Update with the new template
        merge_branch_into_current(repo, template_branch_name)

    # Merge back into current branch
    merge_branch_into_current(repo, merged_branch_name)

    # Current working directory or out root may have been deleted if it was a remove operation
    # and there was nothing else in the folder (git does not save folders without files)
    ensure_exists_folders: List[Union[str, Path]] = [cwd, out_root]
    for folder in ensure_exists_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Folder may have been deleted again while switching branches, so
    # need to set cwd again
    os.chdir(cwd)


def undo_transaction_in_flexlate_branches(
    repo: Repo,
    transaction: FlexlateTransaction,
    merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
    template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
):
    # Reset the template only branch to the appropriate commit
    with temp_repo_that_pushes_to_branch(  # type: ignore
        repo, branch_name=template_branch_name, force_push=True
    ) as temp_repo:
        reset_last_transaction(
            temp_repo, transaction, merged_branch_name, template_branch_name
        )

    # Reset the merged template branch to the appropriate commit
    with temp_repo_that_pushes_to_branch(  # type: ignore
        repo, branch_name=merged_branch_name, force_push=True
    ) as temp_repo:
        reset_last_transaction(
            temp_repo, transaction, merged_branch_name, template_branch_name
        )
