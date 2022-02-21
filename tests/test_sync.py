from typing import Callable

import pytest

from flexlate.config import FlexlateConfig
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import GitRepoDirtyException
from flexlate.syncer import Syncer
from tests.fixtures.templated_repo import *
from tests.fixtures.transaction import sync_transaction


def test_sync_change_in_template_source_name(
    repo_with_cookiecutter_one_template_source: Repo,
    sync_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    expect_name = "new-name"
    config_path = GENERATED_REPO_DIR / "flexlate.json"

    def update_config(config: FlexlateConfig):
        config.template_sources[0].name = expect_name

    # Make a manual change in the template source name
    _update_config(
        config_path, repo, update_config, "Manual change to cookiecutter one name"
    )

    # Sync changes to flexlate branches
    syncer = Syncer()
    syncer.sync_local_changes_to_flexlate_branches(
        repo, sync_transaction, no_input=True
    )

    def check_config(config: FlexlateConfig):
        assert config.template_sources[0].name == expect_name

    _check_config_on_each_branch(config_path, repo, check_config)


def test_sync_change_to_applied_template_root(
    repo_with_template_branch_from_cookiecutter_one_project_add_mode: Repo,
    sync_transaction: FlexlateTransaction,
):
    repo = repo_with_template_branch_from_cookiecutter_one_project_add_mode
    expect_original_output_path = GENERATED_REPO_DIR / "b" / "text.txt"
    expect_new_output_path = GENERATED_REPO_DIR / "a" / "b" / "text.txt"
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    assert expect_original_output_path.exists()

    def update_config(config: FlexlateConfig):
        config.applied_templates[0].root = Path("a")

    # Make a manual change in the template source name
    _update_config(
        config_path,
        repo,
        update_config,
        "Manual change to applied cookiecutter one template location",
    )

    # Sync changes to flexlate branches
    syncer = Syncer()
    syncer.sync_local_changes_to_flexlate_branches(
        repo, sync_transaction, no_input=True
    )

    def check_config(config: FlexlateConfig):
        assert config.applied_templates[0].root == Path("a")

        assert not expect_original_output_path.exists()
        assert expect_new_output_path.exists()

    _check_config_on_each_branch(config_path, repo, check_config)


def test_sync_change_to_applied_template_location(
    repo_with_template_branch_from_cookiecutter_one: Repo,
    sync_transaction: FlexlateTransaction,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    expect_out_path = GENERATED_REPO_DIR / "b" / "text.txt"
    config_path = GENERATED_REPO_DIR / "b" / "flexlate.json"
    new_folder = GENERATED_REPO_DIR / "subdir"
    new_folder.mkdir()
    new_config_path = new_folder / "b" / "flexlate.json"
    new_out_path = new_folder / "b" / "text.txt"
    assert expect_out_path.exists()

    shutil.move(str(GENERATED_REPO_DIR / "b"), new_folder)
    stage_and_commit_all(repo, "Manually move applied template")

    # Sync changes to flexlate branches
    syncer = Syncer()
    syncer.sync_local_changes_to_flexlate_branches(
        repo, sync_transaction, no_input=True
    )

    def check_config(config: FlexlateConfig):
        assert new_out_path.exists()
        assert new_out_path.read_text() == "b"

    _check_config_on_each_branch(new_config_path, repo, check_config)


def test_sync_change_to_data(
    repo_with_template_branch_from_cookiecutter_one: Repo,
    sync_transaction: FlexlateTransaction,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    expect_out_path = GENERATED_REPO_DIR / "b" / "text.txt"
    config_path = GENERATED_REPO_DIR / "b" / "flexlate.json"
    assert expect_out_path.exists()
    assert expect_out_path.read_text() == "b"
    config = FlexlateConfig.load(config_path)
    assert config.applied_templates[0].data == {"a": "b", "c": ""}

    def update_config(config: FlexlateConfig):
        config.applied_templates[0].data = {"a": "b", "c": "d"}

    # Make a manual change in the template source name
    _update_config(
        config_path,
        repo,
        update_config,
        "Manual change to applied cookiecutter one data",
    )

    # Sync changes to flexlate branches
    syncer = Syncer()
    syncer.sync_local_changes_to_flexlate_branches(
        repo, sync_transaction, no_input=True
    )

    def check_config(config: FlexlateConfig):
        assert config.applied_templates[0].data == {"a": "b", "c": "d"}

        assert expect_out_path.exists()
        assert expect_out_path.read_text() == "bd"

    _check_config_on_each_branch(config_path, repo, check_config)


def test_sync_change_to_template_version(
    repo_with_template_branch_from_cookiecutter_remote_version_one: Repo,
    sync_transaction: FlexlateTransaction,
):
    repo = repo_with_template_branch_from_cookiecutter_remote_version_one
    expect_output_path = GENERATED_REPO_DIR / "abc" / "abc.txt"
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    assert expect_output_path.exists()
    assert expect_output_path.read_text() == "value"

    def update_config_for_template_source(config: FlexlateConfig):
        ts = config.template_sources[0]
        ts.target_version = COOKIECUTTER_REMOTE_VERSION_2
        ts.version = COOKIECUTTER_REMOTE_VERSION_2

    # Make a manual change in the template source version
    _update_config(
        config_path,
        repo,
        update_config_for_template_source,
        "Manual change to cookiecutter remote version for template source",
    )

    # Sync changes to flexlate branches
    syncer = Syncer()
    syncer.sync_local_changes_to_flexlate_branches(
        repo, sync_transaction, no_input=True
    )

    def check_config_after_updating_template_source(config: FlexlateConfig):
        ts = config.template_sources[0]
        assert ts.target_version == COOKIECUTTER_REMOTE_VERSION_2
        assert ts.version == COOKIECUTTER_REMOTE_VERSION_2

        assert expect_output_path.exists()
        # Content not updated to version 2, because version was not updated in applied template
        assert expect_output_path.read_text() == "value"

    _check_config_on_each_branch(
        config_path, repo, check_config_after_updating_template_source
    )

    def update_config_for_applied_template(config: FlexlateConfig):
        at = config.applied_templates[0]
        at.version = COOKIECUTTER_REMOTE_VERSION_2

    # Make a manual change in the template source version
    _update_config(
        config_path,
        repo,
        update_config_for_applied_template,
        "Manual change to cookiecutter remote version for applied template",
    )

    # Sync changes to flexlate branches
    syncer.sync_local_changes_to_flexlate_branches(
        repo, sync_transaction, no_input=True
    )

    def check_config_after_updating_applied_template(config: FlexlateConfig):
        at = config.applied_templates[0]
        assert at.version == COOKIECUTTER_REMOTE_VERSION_2

        assert expect_output_path.exists()
        # Content updated to version 2
        assert expect_output_path.read_text() == "some new header\nvalue"

    _check_config_on_each_branch(
        config_path, repo, check_config_after_updating_applied_template
    )


def test_sync_fails_when_there_are_uncommitted_changes(
    repo_with_cookiecutter_one_template_source: Repo,
    sync_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    new_file_path = GENERATED_REPO_DIR / "my-new-file.txt"
    new_file_path.write_text("some text")

    syncer = Syncer()
    with pytest.raises(GitRepoDirtyException):
        syncer.sync_local_changes_to_flexlate_branches(
            repo, sync_transaction, no_input=True
        )


def _check_config_on_each_branch(
    config_path: Path, repo: Repo, checker: Callable[[FlexlateConfig], None]
):
    for branch_name in [
        "master",
        DEFAULT_MERGED_BRANCH_NAME,
        DEFAULT_TEMPLATE_BRANCH_NAME,
    ]:
        branch: Head = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        config = FlexlateConfig.load(config_path)
        checker(config)
    repo.branches["master"].checkout()  # type: ignore


def _update_config(
    config_path: Path,
    repo: Repo,
    updater: Callable[[FlexlateConfig], None],
    commit: str,
):
    config = FlexlateConfig.load(config_path)
    updater(config)
    config.save()
    stage_and_commit_all(repo, commit)
