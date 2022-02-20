from git import Repo

from flexlate.pusher import Pusher
from tests.config import GENERATED_FILES_DIR
from tests.dirutils import assert_dir_trees_are_equal
from tests.fixtures.templated_repo import *
from tests.gitutils import add_remote


def test_push_feature_flexlate_branches(
    repo_with_template_branch_from_cookiecutter_one_and_feature_flexlate_branches: Repo,
):
    repo = repo_with_template_branch_from_cookiecutter_one_and_feature_flexlate_branches
    remote_path = GENERATED_FILES_DIR / "remote"
    remote_path.mkdir()
    remote_repo = Repo.init(remote_path)
    add_remote(repo, remote_path)

    pusher = Pusher()
    pusher.push_feature_flexlate_branches(repo)

    feature_merged_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_TEMPLATE_BRANCH_NAME
    )

    for branch_name in [feature_merged_branch_name, feature_template_branch_name]:
        branch = repo.branches[branch_name]  # type: ignore
        remote_branch = remote_repo.branches[branch_name]  # type: ignore
        branch.checkout()
        remote_branch.checkout()
        assert_dir_trees_are_equal(GENERATED_REPO_DIR, remote_path)
