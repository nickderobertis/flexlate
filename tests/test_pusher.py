import contextlib
from typing import Sequence

from git import Repo

from flexlate.pusher import Pusher
from tests.config import GENERATED_FILES_DIR
from tests.dirutils import assert_dir_trees_are_equal
from tests.fixtures.templated_repo import *
from tests.gitutils import add_remote, add_local_remote


def test_push_feature_flexlate_branches(
    repo_with_template_branch_from_cookiecutter_one_and_feature_flexlate_branches: Repo,
):
    repo = repo_with_template_branch_from_cookiecutter_one_and_feature_flexlate_branches
    feature_merged_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_TEMPLATE_BRANCH_NAME
    )
    pusher = Pusher()
    with add_local_remote_and_check_branches_on_exit(
        repo, [feature_merged_branch_name, feature_template_branch_name]
    ):
        pusher.push_feature_flexlate_branches(repo)


def test_push_main_flexlate_branches(
    repo_with_template_branch_from_cookiecutter_one: Repo,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    pusher = Pusher()
    with add_local_remote_and_check_branches_on_exit(
        repo, [DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME]
    ):
        pusher.push_main_flexlate_branches(repo)


@contextlib.contextmanager
def add_local_remote_and_check_branches_on_exit(
    repo: Repo, branch_names: Sequence[str]
):
    remote_path = GENERATED_FILES_DIR / "remote"
    remote_repo = add_local_remote(repo, remote_path=remote_path)

    yield

    for branch_name in branch_names:
        branch = repo.branches[branch_name]  # type: ignore
        remote_branch = remote_repo.branches[branch_name]  # type: ignore
        branch.checkout()
        remote_branch.checkout()
        assert_dir_trees_are_equal(GENERATED_REPO_DIR, remote_path)
