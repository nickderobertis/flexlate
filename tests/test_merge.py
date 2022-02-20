import pytest

from flexlate.branch_update import (
    get_flexlate_branch_name,
    get_flexlate_branch_name_for_feature_branch,
)
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.merger import Merger
from tests.fixtures.templated_repo import *
from tests.fixtures.template import *
from tests.fixtures.transaction import add_output_transaction
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

    _assert_successful_merge(
        repo, feature_merged_branch_name, feature_template_branch_name, delete
    )


@pytest.mark.parametrize("delete", [True, False])
def test_merge_with_existing_main_branches(
    delete: bool,
    repo_with_template_branch_from_cookiecutter_one: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
):
    repo = repo_with_template_branch_from_cookiecutter_one

    feature_branch_name = "feature"
    feature_merged_branch_name = get_flexlate_branch_name_for_feature_branch(
        feature_branch_name, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name_for_feature_branch(
        feature_branch_name, DEFAULT_TEMPLATE_BRANCH_NAME
    )

    # Existing repo has main flexlate branches. Now do another operation with feature branch
    repo.git.checkout("-b", feature_branch_name)
    subdir = GENERATED_REPO_DIR / "subdir"
    subdir.mkdir()
    with change_directory_to(subdir):
        adder = Adder()
        adder.apply_template_and_add(
            repo,
            cookiecutter_one_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
            merged_branch_name=feature_merged_branch_name,
            template_branch_name=feature_template_branch_name,
        )

    merger = Merger()
    merger.merge_flexlate_branches(repo, delete=delete)

    _assert_successful_merge(
        repo, feature_merged_branch_name, feature_template_branch_name, delete
    )


def _checkout_and_ensure_correct_commit(repo: Repo, branch_name: str):
    branch = repo.branches[branch_name]  # type: ignore
    branch.checkout()
    assert_main_commit_message_matches(
        "Update flexlate templates", repo.commit().message
    )


def _assert_successful_merge(
    repo: Repo,
    feature_merged_branch_name: str,
    feature_template_branch_name: str,
    delete: bool,
):
    for branch_name in [
        "master",
        DEFAULT_MERGED_BRANCH_NAME,
        DEFAULT_TEMPLATE_BRANCH_NAME,
    ]:
        _checkout_and_ensure_correct_commit(repo, branch_name)

    for branch_name in [feature_merged_branch_name, feature_template_branch_name]:
        if delete:
            with pytest.raises(IndexError):
                branch = repo.branches[branch_name]  # type: ignore
        else:
            _checkout_and_ensure_correct_commit(repo, branch_name)
