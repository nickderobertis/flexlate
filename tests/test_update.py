import shutil
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence
from unittest.mock import patch

import pytest
from _pytest.monkeypatch import MonkeyPatch
from git import Repo, Head

from flexlate import branch_update
from flexlate.branch_update import get_flexlate_branch_name_for_feature_branch
from flexlate.config import FlexlateConfig, TemplateSource, TemplateSourceWithTemplates
from flexlate.exc import GitRepoDirtyException
from flexlate.finder.multi import MultiFinder
from flexlate.pusher import Pusher
from flexlate.render.specific import cookiecutter
from flexlate.syncer import Syncer
from flexlate.template.base import Template
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.template.copier import CopierTemplate
from flexlate.template.types import TemplateType
from flexlate.transactions.transaction import FlexlateTransaction
from flexlate.update.main import Updater
from flexlate.update.template import TemplateUpdate
from tests.config import (
    GENERATED_FILES_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_VERSION_1,
    COOKIECUTTER_REMOTE_VERSION_2,
    COOKIECUTTER_ONE_VERSION,
    COOKIECUTTER_ONE_NAME,
)
from tests.fileutils import (
    cookiecutter_one_generated_text_content,
    cookiecutter_two_generated_text_content,
)
from tests.fixtures.git import *
from tests.fixtures.template import *
from tests.fixtures.templated_repo import *
from tests.fixtures.updates import *
from tests.fixtures.local_branch_situation import *
from tests.fixtures.transaction import update_transaction, sync_transaction
from flexlate.ext_git import repo_has_merge_conflicts, delete_local_branch

# TODO: check that config is updated after tests
from tests.gitutils import (
    assert_main_commit_message_matches,
    checkout_new_branch,
    add_local_remote,
)


def test_update_template_dirty_repo(
    cookiecutter_one_update_no_data: TemplateUpdate,
    dirty_repo: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = dirty_repo
    updater = Updater()
    with pytest.raises(GitRepoDirtyException):
        updater.update(
            repo, [cookiecutter_one_update_no_data], update_transaction, no_input=True
        )


def _assert_update_of_cookiecutter_one_modified_template_was_successful(
    repo: Repo,
    main_branch_name: str,
    template_branch_name: str,
    merged_branch_name: str,
):
    main_branch: Head = repo.branches[main_branch_name]  # type: ignore
    merged_branch: Head = repo.branches[merged_branch_name]  # type: ignore
    assert repo.active_branch == main_branch
    assert (
        repo.commit().message
        == f"Merge branch '{template_branch_name}' into {merged_branch_name}\n"
    )
    assert_main_commit_message_matches(
        repo.commit().parents[1].message,
        f"Update flexlate templates\n\none: {COOKIECUTTER_ONE_MODIFIED_VERSION}",
    )
    assert (
        cookiecutter_one_generated_text_content(gen_dir=GENERATED_REPO_DIR)
        == "b and extra"
    )
    assert (GENERATED_REPO_DIR / "ignored" / "ignored.txt").exists()
    assert (GENERATED_REPO_DIR / ".gitignore").exists()
    assert (GENERATED_REPO_DIR / "some-dir" / "placeholder.txt").exists()
    merged_branch.checkout()
    assert repo.active_branch == merged_branch
    assert (
        cookiecutter_one_generated_text_content(gen_dir=GENERATED_REPO_DIR)
        == "b and extra"
    )


def test_update_modify_template(
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_with_gitignore_and_template_branch_from_cookiecutter_one: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_with_gitignore_and_template_branch_from_cookiecutter_one
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_REPO_DIR
    )
    updater.update(repo, template_updates, update_transaction, no_input=True)
    _assert_update_of_cookiecutter_one_modified_template_was_successful(
        repo, "master", DEFAULT_TEMPLATE_BRANCH_NAME, DEFAULT_MERGED_BRANCH_NAME
    )


@pytest.mark.parametrize("target_specific_template", [False, True])
def test_update_modify_specific_template(
    target_specific_template: bool,
    cookiecutter_one_modified_template: CookiecutterTemplate,
    copier_output_subdir_template: CopierTemplate,
    repo_with_gitignore_and_template_branch_from_cookiecutter_one: Repo,
    update_transaction: FlexlateTransaction,
    add_source_transaction: FlexlateTransaction,
    add_output_transaction: FlexlateTransaction,
):
    repo = repo_with_gitignore_and_template_branch_from_cookiecutter_one

    # Add a second template source and output that we are not updating
    adder = Adder()
    with change_directory_to(GENERATED_REPO_DIR):
        adder.add_template_source(
            repo,
            copier_output_subdir_template,
            add_source_transaction,
            out_root=GENERATED_REPO_DIR,
        )
        adder.apply_template_and_add(
            repo,
            copier_output_subdir_template,
            add_output_transaction,
            out_root=GENERATED_REPO_DIR,
            no_input=True,
        )

    updater = Updater()
    update_templates: List[Template]
    if target_specific_template:
        update_templates = [cookiecutter_one_modified_template]
    else:
        update_templates = [
            cookiecutter_one_modified_template,
            copier_output_subdir_template,
        ]
    template_updates = updater.get_updates_for_templates(
        update_templates, project_root=GENERATED_REPO_DIR
    )
    updater.update(repo, template_updates, update_transaction, no_input=True)
    _assert_update_of_cookiecutter_one_modified_template_was_successful(
        repo, "master", DEFAULT_TEMPLATE_BRANCH_NAME, DEFAULT_MERGED_BRANCH_NAME
    )

    # Check to make sure other output was not affected
    output_path = GENERATED_REPO_DIR / "aone.txt"
    assert output_path.read_text() == "atwo"


def test_update_modify_template_with_feature_branches_and_main_branches_are_only_on_remote(
    template_branch_situation: LocalBranchSituation,
    output_branch_situation: LocalBranchSituation,
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_with_gitignore_and_template_branch_from_cookiecutter_one: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_with_gitignore_and_template_branch_from_cookiecutter_one
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_REPO_DIR
    )

    feature_branch = "feature"
    checkout_new_branch(repo, feature_branch)
    feature_merged_branch_name = get_flexlate_branch_name_for_feature_branch(
        feature_branch, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name_for_feature_branch(
        feature_branch, DEFAULT_TEMPLATE_BRANCH_NAME
    )

    # Push to remote and delete local branches, so it will have to fetch from remote to branch off
    add_local_remote(repo)
    pusher = Pusher()
    pusher.push_main_flexlate_branches(repo)
    output_branch_situation.apply(repo, DEFAULT_MERGED_BRANCH_NAME)
    template_branch_situation.apply(repo, DEFAULT_TEMPLATE_BRANCH_NAME)

    updater.update(
        repo,
        template_updates,
        update_transaction,
        no_input=True,
        merged_branch_name=feature_merged_branch_name,
        template_branch_name=feature_template_branch_name,
    )

    # Ensure the output is correct
    _assert_update_of_cookiecutter_one_modified_template_was_successful(
        repo, feature_branch, feature_template_branch_name, feature_merged_branch_name
    )

    # Ensure that flexlate base branches were used properly
    template_branch: Head = repo.branches[feature_template_branch_name]  # type: ignore
    base_template_branch: Head = repo.branches[DEFAULT_TEMPLATE_BRANCH_NAME]  # type: ignore
    assert (
        template_branch.commit.parents[0].hexsha == base_template_branch.commit.hexsha
    )

    output_branch: Head = repo.branches[feature_merged_branch_name]  # type: ignore
    base_output_branch: Head = repo.branches[DEFAULT_MERGED_BRANCH_NAME]  # type: ignore
    assert output_branch.commit.parents[0].hexsha == base_output_branch.commit.hexsha


def test_update_modify_template_with_feature_branches_and_feature_branches_are_only_on_remote(
    template_branch_situation: LocalBranchSituation,
    output_branch_situation: LocalBranchSituation,
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_with_gitignore_and_template_branch_from_cookiecutter_one: Repo,
    update_transaction: FlexlateTransaction,
    sync_transaction: FlexlateTransaction,
):
    repo = repo_with_gitignore_and_template_branch_from_cookiecutter_one
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_REPO_DIR
    )

    feature_branch = "feature"
    checkout_new_branch(repo, feature_branch)
    feature_merged_branch_name = get_flexlate_branch_name_for_feature_branch(
        feature_branch, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name_for_feature_branch(
        feature_branch, DEFAULT_TEMPLATE_BRANCH_NAME
    )

    # Create flexlate feature branches and add commits to distinguish from base flexlate branches
    syncer = Syncer()
    config_path = GENERATED_REPO_DIR / "b" / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    at = config.applied_templates[0]
    at.data = dict(a="b", c="d")
    config.save()
    stage_and_commit_all(repo, "Update data for applied template")
    syncer.sync_local_changes_to_flexlate_branches(
        repo,
        sync_transaction,
        template_branch_name=feature_template_branch_name,
        merged_branch_name=feature_merged_branch_name,
    )

    # Push to remote and delete local branches, so it will have to fetch from remote to branch off
    add_local_remote(repo)
    pusher = Pusher()
    pusher.push_main_flexlate_branches(repo)
    pusher.push_feature_flexlate_branches(repo)

    expect_base_merged_branch_sha = repo.branches[feature_merged_branch_name].commit.hexsha  # type: ignore
    expect_base_template_branch_sha = repo.branches[feature_template_branch_name].commit.hexsha  # type: ignore

    output_branch_situation.apply(repo, DEFAULT_MERGED_BRANCH_NAME)
    output_branch_situation.apply(repo, feature_merged_branch_name)
    template_branch_situation.apply(repo, DEFAULT_TEMPLATE_BRANCH_NAME)
    template_branch_situation.apply(repo, feature_template_branch_name)

    def _resolve_conflicts_then_type_yes(prompt: str) -> bool:
        stage_and_commit_all(repo, "Resolve conflicts")
        return True

    with patch.object(branch_update, "confirm_user", _resolve_conflicts_then_type_yes):
        updater.update(
            repo,
            template_updates,
            update_transaction,
            no_input=True,
            merged_branch_name=feature_merged_branch_name,
            template_branch_name=feature_template_branch_name,
        )

    # Ensure that flexlate base branches were used properly
    template_branch: Head = repo.branches[feature_template_branch_name]  # type: ignore
    assert template_branch.commit.parents[0].hexsha == expect_base_template_branch_sha
    merged_branch: Head = repo.branches[feature_merged_branch_name]  # type: ignore
    assert merged_branch.commit.parents[0].hexsha == expect_base_merged_branch_sha


def test_update_modify_data(
    cookiecutter_one_template: CookiecutterTemplate,
    repo_with_gitignore_and_template_branch_from_cookiecutter_one: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_with_gitignore_and_template_branch_from_cookiecutter_one
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_template],
        data=[{"a": "d", "c": "e"}],
        project_root=GENERATED_REPO_DIR,
    )
    updater.update(repo, template_updates, update_transaction, no_input=True)
    assert (
        cookiecutter_one_generated_text_content(folder="d", gen_dir=GENERATED_REPO_DIR)
        == "de"
    )
    assert (GENERATED_REPO_DIR / "ignored" / "ignored.txt").exists()
    assert (GENERATED_REPO_DIR / ".gitignore").exists()

    # Original b directory should no longer exist, everything moved to d
    assert not (GENERATED_REPO_DIR / "b").exists()

    config_path = GENERATED_REPO_DIR / "d" / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.data == {"a": "d", "c": "e"}


def test_update_modify_data_for_template_in_repo(
    cookiecutter_one_template_in_repo: CookiecutterTemplate,
    repo_with_gitignore_and_template_branch_from_cookiecutter_one_in_repo: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_with_gitignore_and_template_branch_from_cookiecutter_one_in_repo
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_template_in_repo],
        data=[{"a": "d", "c": "e"}],
        project_root=GENERATED_REPO_DIR,
    )
    updater.update(repo, template_updates, update_transaction, no_input=True)
    assert (
        cookiecutter_one_generated_text_content(folder="d", gen_dir=GENERATED_REPO_DIR)
        == "de"
    )
    assert (GENERATED_REPO_DIR / "ignored" / "ignored.txt").exists()
    assert (GENERATED_REPO_DIR / ".gitignore").exists()

    # Original b directory should no longer exist, everything moved to d
    assert not (GENERATED_REPO_DIR / "b").exists()

    config_path = GENERATED_REPO_DIR / "d" / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.data == {"a": "d", "c": "e"}


def test_update_modify_template_conflict(
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_from_cookiecutter_one_with_modifications: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_from_cookiecutter_one_with_modifications
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_FILES_DIR
    )
    manual_commit_message = "Manually resolve conflicts"

    def _resolve_conflicts_then_type_yes(prompt: str) -> bool:
        assert repo_has_merge_conflicts(repo)
        stage_and_commit_all(repo, manual_commit_message)
        return True

    with patch.object(branch_update, "confirm_user", _resolve_conflicts_then_type_yes):
        updater.update(repo, template_updates, update_transaction, no_input=True)


@patch.object(
    cookiecutter, "prompt_for_config", lambda context, no_input: {"a": "b", "c": ""}
)
def test_update_modify_template_conflict_with_resolution(
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_from_cookiecutter_one_with_modifications: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_from_cookiecutter_one_with_modifications
    manual_commit_message = "Manually resolve conflicts"

    def _resolve_conflicts_then_type_yes(prompt: str) -> bool:
        stage_and_commit_all(repo, manual_commit_message)
        return True

    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_FILES_DIR
    )
    with patch.object(branch_update, "confirm_user", _resolve_conflicts_then_type_yes):
        updater.update(repo, template_updates, update_transaction)
    assert not repo_has_merge_conflicts(repo)

    for branch_name in [
        "master",
        DEFAULT_MERGED_BRANCH_NAME,
    ]:
        branch: Head = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        assert repo.commit().message == manual_commit_message + "\n"


@patch.object(
    cookiecutter, "prompt_for_config", lambda context, no_input: {"a": "b", "c": ""}
)
def test_update_modify_template_conflict_with_reject(
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_from_cookiecutter_one_with_modifications: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_from_cookiecutter_one_with_modifications

    def _reject_update(prompt: str) -> bool:
        return False

    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_FILES_DIR
    )
    with patch.object(branch_update, "confirm_user", _reject_update):
        updater.update(repo, template_updates, update_transaction)

    assert repo.commit().message == "Prepend cookiecutter text with hello\n"

    for branch_name in [DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME]:
        branch: Head = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        assert_main_commit_message_matches(
            repo.commit().message, "Update flexlate templates"
        )


@patch.object(
    cookiecutter, "prompt_for_config", lambda context, no_input: {"a": "b", "c": ""}
)
def test_update_modify_template_conflict_with_reject_on_feature_branches(
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_from_cookiecutter_one_with_modifications: Repo,
    update_transaction: FlexlateTransaction,
):
    repo = repo_from_cookiecutter_one_with_modifications

    def _reject_update(prompt: str) -> bool:
        return False

    feature_branch = "feature"
    checkout_new_branch(repo, feature_branch)

    feature_merged_branch_name = get_flexlate_branch_name_for_feature_branch(
        feature_branch, DEFAULT_MERGED_BRANCH_NAME
    )
    feature_template_branch_name = get_flexlate_branch_name_for_feature_branch(
        feature_branch, DEFAULT_TEMPLATE_BRANCH_NAME
    )

    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_FILES_DIR
    )
    with patch.object(branch_update, "confirm_user", _reject_update):
        updater.update(
            repo,
            template_updates,
            update_transaction,
            merged_branch_name=feature_merged_branch_name,
            template_branch_name=feature_template_branch_name,
        )

    assert repo.commit().message == "Prepend cookiecutter text with hello\n"

    # Main branches are at original state
    for branch_name in [DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME]:
        branch: Head = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        assert_main_commit_message_matches(
            repo.commit().message, "Update flexlate templates"
        )

    # Feature branches are now deleted
    for branch_name in [feature_template_branch_name, feature_merged_branch_name]:
        with pytest.raises(IndexError):
            branch = repo.branches[branch_name]  # type: ignore


@pytest.mark.parametrize(
    "remote_target_version", [None, "main", COOKIECUTTER_REMOTE_VERSION_2]
)
def test_update_passed_templates_to_newest_versions(
    remote_target_version: Optional[str],
    cookiecutter_one_template: CookiecutterTemplate,
    update_transaction: FlexlateTransaction,
):
    wipe_generated_folder()
    local_template = cookiecutter_one_template
    _modify_cookiecutter_one_template_in_generated_folder(local_template)
    updater = Updater()
    finder = MultiFinder()
    remote_template = finder.find(
        COOKIECUTTER_REMOTE_URL, version=COOKIECUTTER_REMOTE_VERSION_1
    )

    class MockConfigManager:
        def get_sources_with_templates(
            self,
            templates: Sequence[Template],
            project_root: Path = Path("."),
            config: Optional[FlexlateConfig] = None,
        ) -> List[TemplateSourceWithTemplates]:
            return [
                TemplateSourceWithTemplates(
                    source=TemplateSource.from_template(
                        remote_template, target_version=remote_target_version
                    ),
                    templates=[remote_template],
                ),
                TemplateSourceWithTemplates(
                    source=TemplateSource.from_template(local_template),
                    templates=[local_template],
                ),
            ]

    assert remote_template.version == COOKIECUTTER_REMOTE_VERSION_1
    assert local_template.version == COOKIECUTTER_ONE_VERSION
    updater.update_passed_templates_to_target_versions(
        [remote_template, local_template], update_transaction, config_manager=MockConfigManager()  # type: ignore
    )
    assert remote_template.version == COOKIECUTTER_REMOTE_VERSION_2
    assert local_template.version == "471c7dbeea2541fe9a7a558d3aafb6e0"


def test_update_passed_templates_to_newest_versions_but_already_at_targets(
    cookiecutter_one_template: CookiecutterTemplate,
    update_transaction: FlexlateTransaction,
):
    wipe_generated_folder()
    local_template = cookiecutter_one_template
    _modify_cookiecutter_one_template_in_generated_folder(local_template)
    updater = Updater()
    finder = MultiFinder()
    remote_template = finder.find(
        COOKIECUTTER_REMOTE_URL, version=COOKIECUTTER_REMOTE_VERSION_1
    )

    class MockConfigManager:
        def get_sources_with_templates(
            self,
            templates: Sequence[Template],
            project_root: Path = Path("."),
            config: Optional[FlexlateConfig] = None,
        ) -> List[TemplateSourceWithTemplates]:
            return [
                TemplateSourceWithTemplates(
                    source=TemplateSource.from_template(
                        remote_template, target_version=COOKIECUTTER_REMOTE_VERSION_1
                    ),
                    templates=[remote_template],
                ),
                TemplateSourceWithTemplates(
                    # It is actually useless to put target version in a local template
                    # TODO: throw an error when user tries to target version for a local template
                    source=TemplateSource.from_template(
                        local_template, target_version=COOKIECUTTER_ONE_VERSION
                    ),
                    templates=[local_template],
                ),
            ]

    assert remote_template.version == COOKIECUTTER_REMOTE_VERSION_1
    assert local_template.version == COOKIECUTTER_ONE_VERSION
    updater.update_passed_templates_to_target_versions(
        [remote_template, local_template], update_transaction, config_manager=MockConfigManager()  # type: ignore
    )
    assert remote_template.version == COOKIECUTTER_REMOTE_VERSION_1
    # Local template is updated anyway, but it shows the old version due to target version
    assert local_template.version == COOKIECUTTER_ONE_VERSION


def _modify_cookiecutter_one_template_in_generated_folder(template: Template):
    template_folder = GENERATED_FILES_DIR / COOKIECUTTER_ONE_NAME
    shutil.copytree(template.path, template_folder, dirs_exist_ok=True)
    template.path = template_folder
    (template_folder / "some file.txt").touch()
