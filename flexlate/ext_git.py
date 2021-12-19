import os
from contextlib import contextmanager
from pathlib import Path
from typing import cast, Set

from git import Repo, Blob, Tree, GitCommandError  # type: ignore

from flexlate.exc import GitRepoDirtyException, GitRepoHasNoCommitsException


def checkout_template_branch(repo: Repo, branch_name: str):
    try:
        # Get branch if it exists already
        branch = repo.branches[branch_name]  # type: ignore
    except IndexError as e:
        if "No item found with id" in str(e) and branch_name in str(e):
            # Could not find branch, must not exist, create it
            # Get the initial root commit to base it off of
            initial_commit = repo.git.rev_list("HEAD", max_parents=0)
            branch = repo.create_head(branch_name, initial_commit)
        else:
            # Unknown error, raise it
            raise e

    branch.checkout()


def stage_and_commit_all(repo: Repo, commit_message: str):
    repo.git.add("-A")
    repo.git.commit("-m", commit_message)


def merge_branch_into_current(
    repo: Repo, branch_name: str, allow_conflicts: bool = True
):
    try:
        repo.git.merge(branch_name)
    except GitCommandError as e:
        if allow_conflicts and "fix conflicts and then commit the result" in e.stdout:
            #
            return
        raise e


def get_current_version(repo: Repo) -> str:
    return repo.head.commit.hexsha

# TODO: rework template branch update process
#  For the template branch
#  1. Clone the local repo into a temporary directory, but only the templates branch
#  - git clone <project path> --branch <template branch> --single-branch <temp dir>
#  2. Wipe all non-flexlate files in the temp dir
#  3. Render templates in temp dir
#  4. from temp dir: git push <project path> <template branch>
#  For the merged branch
#  - Before checking out the branch, fast forward it without checking out via
#  `git fetch . <current branch>:<merged branch>`

@contextmanager
def checked_out_template_branch(repo: Repo, branch_name: str):
    orig_branch = repo.active_branch
    checkout_template_branch(repo, branch_name=branch_name)
    yield
    orig_branch.checkout()


def repo_has_merge_conflicts(repo: Repo) -> bool:
    for path, blob_tuples in repo.index.unmerged_blobs().items():
        for (code, blob) in blob_tuples:
            if code != 0:
                # Code 0 means merged successfully. 1, 2, and 3 represent conflicts
                return True
    return False


def assert_repo_is_in_clean_state(repo: Repo):
    if repo.is_dirty(untracked_files=True):
        raise GitRepoDirtyException(
            "git working tree is not clean. Please commit, stash, or discard any changes first."
        )
    if repo.git.count_objects() == "0 objects, 0 kilobytes":
        # Empty repo, no commits
        raise GitRepoHasNoCommitsException(
            "git repo has no commits. Please initialize it with a commit"
        )
