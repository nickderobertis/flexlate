import os
from pathlib import Path
from typing import List, cast, Set

from git import Repo, Blob, Tree

DEFAULT_BRANCH_NAME = "flexlate-output"


def checkout_template_branch(repo: Repo, branch_name: str = DEFAULT_BRANCH_NAME):
    try:
        # Get branch if it exists already
        branch = repo.branches[branch_name]  # type: ignore
    except IndexError as e:
        if "No item found with id" in str(e) and branch_name in str(e):
            # Could not find branch, must not exist, create it
            branch = repo.create_head(branch_name)
        else:
            # Unknown error, raise it
            raise e

    branch.checkout()


def stage_and_commit_all(repo: Repo, commit_message: str):
    repo.git.add(".")
    repo.git.commit("-m", commit_message)


def list_tracked_files(repo: Repo) -> Set[Path]:
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
        os.remove(path)


def merge_branch_into_current(repo: Repo, branch_name: str):
    repo.git.merge(branch_name)


def get_current_version(repo: Repo) -> str:
    return repo.head.commit.hexsha