import pytest

from flexlate.branch_update import get_flexlate_branch_name
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.merger import Merger
from tests.fixtures.templated_repo import *
from tests.gitutils import rename_branch, assert_main_commit_message_matches


@pytest.mark.parametrize("delete", [True, False])
def test_merge_with_non_existent_main_branches(
    delete: bool,
    repo_with_template_branch_from_cookiecutter_one: Repo,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    # Simulate conditions of developing on feature branch
    feature_merged_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_TEMPLATE_BRANCH_NAME
    )
    rename_branch(repo, DEFAULT_MERGED_BRANCH_NAME, feature_merged_branch_name)
    rename_branch(repo, DEFAULT_TEMPLATE_BRANCH_NAME, feature_template_branch_name)

    merger = Merger()
    merger.merge_flexlate_branches(repo, delete=delete)

    def checkout_and_ensure_correct_commit(branch_name: str):
        branch = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        assert_main_commit_message_matches(
            "Update flexlate templates", repo.commit().message
        )

    for branch_name in [
        "master",
        DEFAULT_MERGED_BRANCH_NAME,
        DEFAULT_TEMPLATE_BRANCH_NAME,
    ]:
        checkout_and_ensure_correct_commit(branch_name)

    for branch_name in [feature_merged_branch_name, feature_template_branch_name]:
        if delete:
            with pytest.raises(IndexError):
                branch = repo.branches[branch_name]  # type: ignore
        else:
            checkout_and_ensure_correct_commit(branch_name)
