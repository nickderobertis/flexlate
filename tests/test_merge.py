import re
from unittest.mock import patch

import pytest

from flexlate.branch_update import (
    get_flexlate_branch_name,
    get_flexlate_branch_name_for_feature_branch,
)
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.ext_git import merge_branch_into_current
from flexlate.merger import Merger
from flexlate import merger as merger_mod
from tests.fixtures.templated_repo import *
from tests.fixtures.template import *
from tests.fixtures.transaction import add_output_transaction
from tests.gitutils import (
    rename_branch,
    assert_main_commit_message_matches,
    checkout_new_branch,
)


@pytest.mark.parametrize("delete", [True, False])
def test_merge_with_non_existent_main_branches(
    delete: bool,
    repo_with_template_branch_from_cookiecutter_one_and_feature_flexlate_branches: Repo,
):
    repo = repo_with_template_branch_from_cookiecutter_one_and_feature_flexlate_branches
    feature_merged_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name(
        repo, DEFAULT_TEMPLATE_BRANCH_NAME
    )

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
    checkout_new_branch(repo, feature_branch_name)
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


@pytest.mark.parametrize("delete", [True, False])
@pytest.mark.parametrize("commit_first", [True, False])
def test_merge_with_existing_main_branches_and_conflicts(
    delete: bool,
    commit_first: bool,
    repo_with_template_branch_from_cookiecutter_one: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
):
    repo = repo_with_template_branch_from_cookiecutter_one

    adder = Adder()
    merger = Merger()

    # Existing repo has main flexlate branches. Now do another operation with feature branch
    subdir = GENERATED_REPO_DIR / "subdir"
    subdir.mkdir()
    with change_directory_to(subdir):
        for i in range(2):
            feature_branch_name = f"feature-{i + 1}"
            data = dict(a=str(i), c=str(i))
            feature_merged_branch_name = get_flexlate_branch_name_for_feature_branch(
                feature_branch_name, DEFAULT_MERGED_BRANCH_NAME
            )
            feature_template_branch_name = get_flexlate_branch_name_for_feature_branch(
                feature_branch_name, DEFAULT_TEMPLATE_BRANCH_NAME
            )
            checkout_new_branch(repo, feature_branch_name)
            adder.apply_template_and_add(
                repo,
                cookiecutter_one_template,
                add_output_transaction,
                out_root=GENERATED_REPO_DIR,
                no_input=True,
                data=data,
                add_mode=AddMode.PROJECT,
                merged_branch_name=feature_merged_branch_name,
                template_branch_name=feature_template_branch_name,
            )
            repo.git.checkout("master")

    merger.merge_flexlate_branches(repo, "feature-1", delete=delete)
    merge_branch_into_current(repo, "feature-1")

    manual_commit_message = "Manually resolve conflicts"

    def _resolve_conflicts_then_type_yes(prompt: str) -> bool:
        # Prompt will be coming and may or may not have a temp repo location
        # Need to get reference to temp repo, parse message to do so
        pattern = re.compile(r"Successfully handled conflicts in ([\/\d\w]+)\?")
        match = pattern.search(prompt)

        if match:
            # This means we are operating on the temp_repo (template branch)
            tmp_dir = match.group(1)
            use_repo = Repo(tmp_dir)
        else:
            # This means we are operating on the main repo (merged branch)
            use_repo = repo

        stage_and_commit_all(use_repo, manual_commit_message)
        return True

    if commit_first:
        merge_branch_into_current(repo, "feature-2")
        stage_and_commit_all(repo, manual_commit_message)

    with patch.object(merger_mod, "confirm_user", _resolve_conflicts_then_type_yes):
        merger.merge_flexlate_branches(repo, "feature-2", delete=delete)

    if not commit_first:
        merge_branch_into_current(repo, "feature-2")
        stage_and_commit_all(repo, manual_commit_message)

    _assert_successful_merge(
        repo,
        get_flexlate_branch_name_for_feature_branch(
            "feature-2", DEFAULT_MERGED_BRANCH_NAME
        ),
        get_flexlate_branch_name_for_feature_branch(
            "feature-2", DEFAULT_TEMPLATE_BRANCH_NAME
        ),
        delete,
        main_branch_message=manual_commit_message,
    )


def _checkout_and_ensure_correct_commit(
    repo: Repo, branch_name: str, message: str = "Update flexlate templates"
):
    branch = repo.branches[branch_name]  # type: ignore
    branch.checkout()
    assert_main_commit_message_matches(message, repo.commit().message)


def _assert_successful_merge(
    repo: Repo,
    feature_merged_branch_name: str,
    feature_template_branch_name: str,
    delete: bool,
    feature_branch_message: str = "Update flexlate templates",
    main_branch_message: str = "Update flexlate templates",
):
    for branch_name in [
        "master",
        DEFAULT_MERGED_BRANCH_NAME,
        DEFAULT_TEMPLATE_BRANCH_NAME,
    ]:
        _checkout_and_ensure_correct_commit(
            repo, branch_name, message=main_branch_message
        )

    for branch_name in [feature_merged_branch_name, feature_template_branch_name]:
        if delete:
            with pytest.raises(IndexError):
                branch = repo.branches[branch_name]  # type: ignore
        else:
            _checkout_and_ensure_correct_commit(
                repo, branch_name, message=feature_branch_message
            )
