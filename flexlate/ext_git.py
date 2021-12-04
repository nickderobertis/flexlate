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


def list_tracked_files(repo: Repo) -> Set[Path]:
    if repo.working_dir is None:
        raise ValueError("repo working dir should not be none")
    return _list_tracked_files(repo.tree(), Path(repo.working_dir))


def _list_tracked_files(tree: Tree, root_path: Path) -> Set[Path]:
    # TODO: Fix multiple iterations over files for git traverse
    #  For now just using a set to keep it working, but should optimize
    files: Set[Path] = set()
    for tree_or_blob in tree.traverse():
        if hasattr(tree_or_blob, "traverse"):
            # Got another tree
            tree = cast(Tree, tree_or_blob)
            files.update(_list_tracked_files(tree, root_path))
        else:
            # Got a blob
            blob = cast(Blob, tree_or_blob)
            files.add(root_path / Path(blob.path))
    return files


def delete_tracked_files(repo: Repo):
    for path in list_tracked_files(repo):
        if path.name == "flexlate.json":
            continue
        os.remove(path)


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
