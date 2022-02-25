import os
from pathlib import Path
from typing import Callable, Union, List, Optional

from git import Repo, repo, Head

from flexlate.cli_utils import confirm_user
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import (
    temp_repo_that_pushes_to_branch,
    stage_and_commit_all,
    fast_forward_branch_without_checkout,
    checked_out_template_branch,
    merge_branch_into_current,
    abort_merge,
    reset_branch_to_commit_without_checkout,
    repo_has_merge_conflicts,
    get_branch_sha,
)
from flexlate.path_ops import make_func_that_creates_cwd_and_out_root_before_running
from flexlate.styles import (
    print_styled,
    ACTION_REQUIRED_STYLE,
    styled,
    QUESTION_STYLE,
    ALERT_STYLE,
)
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
    base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
    template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    remote: str = "origin",
):
    cwd = os.getcwd()
    current_branch = repo.active_branch

    # Save the status of the flexlate branches. We may need to roll back to this state
    # if the user aborts the operation
    merged_branch_sha = get_branch_sha(repo, merged_branch_name)
    template_branch_sha = get_branch_sha(repo, template_branch_name)

    make_dirs_add_operation = make_func_that_creates_cwd_and_out_root_before_running(
        out_root, file_operation
    )

    # Update the template only branch with the new template
    with temp_repo_that_pushes_to_branch(  # type: ignore
        repo,
        branch_name=template_branch_name,
        base_branch_name=base_template_branch_name,
        remote=remote,
    ) as temp_repo:
        make_dirs_add_operation(Path(temp_repo.working_dir))  # type: ignore
        stage_and_commit_all(temp_repo, commit_message)

    # Bring the change into the merged branch
    # Update with changes from the main repo
    fast_forward_branch_without_checkout(repo, merged_branch_name, current_branch.name)
    with checked_out_template_branch(
        repo, branch_name=merged_branch_name, base_branch_name=base_merged_branch_name
    ):
        # Update with the new template
        merge_branch_into_current(repo, template_branch_name)
        if repo_has_merge_conflicts(repo):
            aborted = prompt_to_fix_conflicts_and_reset_on_abort_return_aborted(
                repo,
                current_branch,
                merged_branch_sha,
                template_branch_sha,
                merged_branch_name,
                template_branch_name,
            )
            if aborted:
                return

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
    base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
    template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
    base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
):
    # Reset the template only branch to the appropriate commit
    with temp_repo_that_pushes_to_branch(  # type: ignore
        repo,
        branch_name=template_branch_name,
        base_branch_name=base_template_branch_name,
        force_push=True,
    ) as temp_repo:
        reset_last_transaction(
            temp_repo, transaction, merged_branch_name, template_branch_name
        )

    # Reset the merged template branch to the appropriate commit
    with temp_repo_that_pushes_to_branch(  # type: ignore
        repo,
        branch_name=merged_branch_name,
        base_branch_name=base_merged_branch_name,
        force_push=True,
    ) as temp_repo:
        reset_last_transaction(
            temp_repo, transaction, merged_branch_name, template_branch_name
        )


def abort_merge_and_reset_flexlate_branches(
    repo: Repo,
    current_branch: Head,
    merged_branch_sha: Optional[str] = None,
    template_branch_sha: Optional[str] = None,
    merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
    template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
):
    abort_merge(repo)
    current_branch.checkout()
    reset_branch_to_commit_without_checkout(repo, merged_branch_name, merged_branch_sha)
    reset_branch_to_commit_without_checkout(
        repo, template_branch_name, template_branch_sha
    )


def prompt_to_fix_conflicts_and_reset_on_abort_return_aborted(
    repo: Repo,
    current_branch: Head,
    merged_branch_sha: Optional[str],
    template_branch_sha: Optional[str],
    merged_branch_name: str,
    template_branch_name: str,
) -> bool:
    print_styled(
        "Repo has merge conflicts after update, please resolve them",
        ACTION_REQUIRED_STYLE,
    )
    user_fixed = confirm_user(styled("Conflicts fixed? n to abort", QUESTION_STYLE))
    if not user_fixed:
        print_styled(
            "Aborting update.",
            ALERT_STYLE,
        )
        abort_merge_and_reset_flexlate_branches(
            repo,
            current_branch,
            merged_branch_sha=merged_branch_sha,
            template_branch_sha=template_branch_sha,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
        )
        return True
    return False


def get_flexlate_branch_name(repo: Repo, base_branch_name: str) -> str:
    current_branch = repo.active_branch.name
    return get_flexlate_branch_name_for_feature_branch(current_branch, base_branch_name)


def get_flexlate_branch_name_for_feature_branch(
    feature_branch: str, base_branch_name: str
) -> str:
    return f"{base_branch_name}-{feature_branch}"
