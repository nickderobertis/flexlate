from unittest.mock import patch

from git import Repo

from flexlate import branch_update
from flexlate.bootstrapper import Bootstrapper
from flexlate.config import FlexlateProjectConfig
from tests.fixtures.templated_repo import *
from tests.fixtures.transaction import bootstrap_transaction
from tests.fs_checks import (
    assert_template_source_cookiecutter_one_added_correctly,
    assert_cookiecutter_one_applied_template_added_correctly,
    assert_project_config_is_correct,
)


def test_bootstrap_cookiecutter_one(
    repo_with_cookiecutter_one_applied_but_no_flexlate: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    bootstrap_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_applied_but_no_flexlate
    template = cookiecutter_one_template

    bootstrapper = Bootstrapper()
    bootstrapper.bootstrap_flexlate_init_from_existing_template(
        repo, template, bootstrap_transaction, no_input=True, data=dict(a="b", c="")
    )

    # Check that all Flexlate config files are correct
    assert_template_source_cookiecutter_one_added_correctly(cookiecutter_one_template)
    assert_cookiecutter_one_applied_template_added_correctly(
        template, GENERATED_REPO_DIR / "b"
    )
    assert_project_config_is_correct()

    _assert_flexlate_merge_branch_exists_and_is_up_to_date(repo)


def test_bootstrap_cookiecutter_one_with_conflicts(
    repo_with_cookiecutter_one_applied_but_no_flexlate: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    bootstrap_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_applied_but_no_flexlate
    template = cookiecutter_one_template

    # Modify templated output to cause conflict
    content_path = GENERATED_REPO_DIR / "b" / "text.txt"
    content_path.write_text("merge conflict")
    stage_and_commit_all(
        repo, "Add a change that should cause a merge conflict on bootstrap"
    )

    bootstrapper = Bootstrapper()

    def _resolve_conflicts_then_type_yes(prompt: str) -> bool:
        stage_and_commit_all(repo, "Resolve conflicts")
        return True

    with patch.object(branch_update, "confirm_user", _resolve_conflicts_then_type_yes):
        bootstrapper.bootstrap_flexlate_init_from_existing_template(
            repo, template, bootstrap_transaction, no_input=True, data=dict(a="b", c="")
        )

    # Check that all Flexlate config files are correct
    assert_template_source_cookiecutter_one_added_correctly(cookiecutter_one_template)
    assert_cookiecutter_one_applied_template_added_correctly(
        template, GENERATED_REPO_DIR / "b"
    )
    assert_project_config_is_correct()

    _assert_flexlate_merge_branch_exists_and_is_up_to_date(repo)


def _assert_flexlate_merge_branch_exists_and_is_up_to_date(repo: Repo):
    master = repo.active_branch
    merged_branch = repo.branches[DEFAULT_MERGED_BRANCH_NAME]  # type: ignore
    assert merged_branch.commit.hexsha == master.commit.hexsha
