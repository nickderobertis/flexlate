import os
from unittest.mock import patch

from flexlate import branch_update
from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig
from flexlate.exc import (
    CannotRemoveTemplateSourceException,
    CannotRemoveAppliedTemplateException,
)
from flexlate.ext_git import repo_has_merge_conflicts
from flexlate.remover import Remover
from flexlate.transactions.transaction import FlexlateTransaction
from tests.config import (
    COOKIECUTTER_ONE_NAME,
    COOKIECUTTER_TWO_NAME,
    COOKIECUTTER_REMOTE_NAME,
)
from tests.fixtures.templated_repo import *
from tests.fixtures.transaction import (
    remove_source_transaction,
    remove_output_transaction,
    add_source_transaction,
)
from tests.gitutils import accept_theirs_in_merge_conflict


def test_remove_template_source(
    repo_with_cookiecutter_one_template_source: Repo,
    remove_source_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    remover = Remover()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        assert config_path.exists()
        remover.remove_template_source(
            repo, COOKIECUTTER_ONE_NAME, remove_source_transaction
        )
        assert not config_path.exists()


def test_remove_template_source_when_multiple_exist(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_two_template: CookiecutterTemplate,
    remove_source_transaction: FlexlateTransaction,
    add_source_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    remover = Remover()
    adder = Adder()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        adder.add_template_source(
            repo, cookiecutter_two_template, add_source_transaction
        )
        remover.remove_template_source(
            repo, COOKIECUTTER_ONE_NAME, remove_source_transaction
        )

    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0
    assert len(config.template_sources) == 1
    template_source = config.template_sources[0]
    assert template_source.name == COOKIECUTTER_TWO_NAME


def test_remove_template_source_when_outputs_from_another_source_exist(
    repo_with_cookiecutter_one_template_source_and_output: Repo,
    cookiecutter_two_template: CookiecutterTemplate,
    remove_source_transaction: FlexlateTransaction,
    add_source_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source_and_output
    remover = Remover()
    adder = Adder()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    with change_directory_to(GENERATED_REPO_DIR):
        adder.add_template_source(
            repo, cookiecutter_two_template, add_source_transaction
        )
        remover.remove_template_source(
            repo, COOKIECUTTER_TWO_NAME, remove_source_transaction
        )

    # Check source successfully removed
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0
    assert len(config.template_sources) == 1
    template_source = config.template_sources[0]
    assert template_source.name == COOKIECUTTER_ONE_NAME

    # Check no side effects
    unrelated_config_path = GENERATED_REPO_DIR / "b" / "flexlate.json"
    config = FlexlateConfig.load(unrelated_config_path)
    assert len(config.template_sources) == 0
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.add_mode == AddMode.LOCAL
    assert at.version == COOKIECUTTER_ONE_VERSION
    assert at.data == {"a": "b", "c": ""}
    assert at.name == "one"
    assert at.root == Path("..")


def test_remove_non_existing_template_source(
    repo_with_placeholder_committed: Repo,
    remove_source_transaction: FlexlateTransaction,
):
    repo = repo_with_placeholder_committed
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        with pytest.raises(CannotRemoveTemplateSourceException) as exc_info:
            remover.remove_template_source(
                repo, COOKIECUTTER_ONE_NAME, remove_source_transaction
            )
        assert "Cannot find any template source" in str(exc_info.value)


def test_remove_template_source_when_output_exists(
    repo_with_cookiecutter_one_template_source_and_output: Repo,
    remove_source_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source_and_output
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        with pytest.raises(CannotRemoveTemplateSourceException) as exc_info:
            remover.remove_template_source(
                repo, COOKIECUTTER_ONE_NAME, remove_source_transaction
            )
        assert "has existing outputs" in str(exc_info.value)


def test_remove_template_source_with_merge_conflict_resolution(
    repo_with_cookiecutter_remote_version_one_template_source_that_will_have_merge_conflict_on_flexlate_operation: Repo,
    remove_source_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_remote_version_one_template_source_that_will_have_merge_conflict_on_flexlate_operation
    remover = Remover()
    config_path = GENERATED_REPO_DIR / "flexlate.json"

    def _resolve_conflicts_then_type_yes(prompt: str) -> bool:
        assert repo_has_merge_conflicts(repo)
        os.remove(config_path)
        stage_and_commit_all(repo, "Manually resolve conflicts")
        return True

    with change_directory_to(GENERATED_REPO_DIR):
        assert config_path.exists()
        with patch.object(
            branch_update, "confirm_user", _resolve_conflicts_then_type_yes
        ):
            remover.remove_template_source(
                repo, COOKIECUTTER_REMOTE_NAME, remove_source_transaction
            )
        assert not config_path.exists()


def test_remove_applied_template(
    repo_with_template_branch_from_cookiecutter_one: Repo,
    remove_output_transaction: FlexlateTransaction,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    remover = Remover()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    output_path = GENERATED_REPO_DIR / "b" / "text.txt"
    with change_directory_to(GENERATED_REPO_DIR):
        assert output_path.read_text() == "b"
        remover.remove_applied_template_and_output(
            repo, COOKIECUTTER_ONE_NAME, remove_output_transaction
        )

    assert not output_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 1
    assert len(config.applied_templates) == 0


def test_remove_applied_template_that_does_not_exist(
    repo_with_cookiecutter_one_template_source: Repo,
    remove_output_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    remover = Remover()
    with change_directory_to(GENERATED_REPO_DIR):
        with pytest.raises(CannotRemoveAppliedTemplateException) as exc_info:
            remover.remove_applied_template_and_output(
                repo, COOKIECUTTER_ONE_NAME, remove_output_transaction
            )
        assert "Cannot find any applied template with name" in str(exc_info.value)


def test_remove_applied_template_when_multiple_exist(
    repo_with_cookiecutter_one_template_source_and_output: Repo,
    remove_output_transaction: FlexlateTransaction,
    add_output_transaction: FlexlateTransaction,
    cookiecutter_one_template: CookiecutterTemplate,
):
    repo = repo_with_cookiecutter_one_template_source_and_output
    remover = Remover()
    adder = Adder()
    subdir = GENERATED_REPO_DIR / "subdir"
    subdir.mkdir()
    config_path = subdir / "b" / "flexlate.json"
    output_path = subdir / "b" / "text.txt"
    with change_directory_to(subdir):
        adder.apply_template_and_add(
            repo, cookiecutter_one_template, add_output_transaction, no_input=True
        )
        assert output_path.read_text() == "b"
        assert config_path.exists()
        remover.remove_applied_template_and_output(
            repo, COOKIECUTTER_ONE_NAME, remove_output_transaction
        )

    # Ensure that remove went correctly
    assert not output_path.exists()
    assert not config_path.exists()

    # Ensure no side effects
    unrelated_config_path = GENERATED_REPO_DIR / "b" / "flexlate.json"
    config = FlexlateConfig.load(unrelated_config_path)
    assert len(config.template_sources) == 0
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.add_mode == AddMode.LOCAL
    assert at.version == COOKIECUTTER_ONE_VERSION
    assert at.data == {"a": "b", "c": ""}
    assert at.name == "one"
    assert at.root == Path("..")


def test_remove_applied_template_with_merge_conflict_resolution(
    repo_with_cookiecutter_remote_version_one_template_source_and_output_that_will_have_merge_conflict_on_flexlate_operation: Repo,
    remove_output_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_remote_version_one_template_source_and_output_that_will_have_merge_conflict_on_flexlate_operation
    remover = Remover()
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    output_path = GENERATED_REPO_DIR / "abc" / "abc.txt"

    def _resolve_conflicts_then_type_yes(prompt: str) -> bool:
        assert repo_has_merge_conflicts(repo)
        accept_theirs_in_merge_conflict(repo)
        stage_and_commit_all(repo, "Manually resolve conflicts")
        return True

    with change_directory_to(GENERATED_REPO_DIR):
        assert output_path.read_text() == "some new header\nvalue"
        with patch.object(
            branch_update, "confirm_user", _resolve_conflicts_then_type_yes
        ):
            remover.remove_applied_template_and_output(
                repo,
                COOKIECUTTER_REMOTE_NAME,
                remove_output_transaction,
                add_mode=AddMode.PROJECT,
            )

    assert not output_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 1
    assert len(config.applied_templates) == 0
