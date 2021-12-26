import shutil
import tempfile
from pathlib import Path
from typing import Optional, Sequence
from unittest.mock import patch

import pytest
from git import Repo, Head

from flexlate.config import FlexlateConfig, TemplateSource
from flexlate.exc import GitRepoDirtyException
from flexlate.finder.multi import MultiFinder
from flexlate.template.base import Template
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME
from flexlate.template.types import TemplateType
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
from flexlate.ext_git import repo_has_merge_conflicts


# TODO: check that config is updated after tests


def test_update_template_dirty_repo(
    cookiecutter_one_update_no_data: TemplateUpdate,
    dirty_repo: Repo,
):
    repo = dirty_repo
    updater = Updater()
    with pytest.raises(GitRepoDirtyException):
        updater.update(repo, [cookiecutter_one_update_no_data], no_input=True)


def test_update_modify_template(
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_with_gitignore_and_template_branch_from_cookiecutter_one: Repo,
):
    repo = repo_with_gitignore_and_template_branch_from_cookiecutter_one
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_REPO_DIR
    )
    updater.update(repo, template_updates, no_input=True)
    main_branch: Head = repo.branches["master"]  # type: ignore
    template_branch: Head = repo.branches[DEFAULT_MERGED_BRANCH_NAME]  # type: ignore
    assert repo.active_branch == main_branch
    assert (
        repo.commit().message
        == "Merge branch 'flexlate-templates' into flexlate-output\n"
    )
    assert (
        repo.commit().parents[1].message
        == f"Update flexlate templates\n\none: {COOKIECUTTER_ONE_MODIFIED_VERSION}\n"
    )
    assert (
        cookiecutter_one_generated_text_content(gen_dir=GENERATED_REPO_DIR)
        == "b and extra"
    )
    assert (GENERATED_REPO_DIR / "ignored" / "ignored.txt").exists()
    assert (GENERATED_REPO_DIR / ".gitignore").exists()
    template_branch.checkout()
    assert repo.active_branch == template_branch
    assert (
        cookiecutter_one_generated_text_content(gen_dir=GENERATED_REPO_DIR)
        == "b and extra"
    )


def test_update_modify_template_conflict(
    cookiecutter_one_modified_template: CookiecutterTemplate,
    repo_from_cookiecutter_one_with_modifications: Repo,
):
    repo = repo_from_cookiecutter_one_with_modifications
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_FILES_DIR
    )
    updater.update(repo, template_updates, no_input=True)
    assert repo_has_merge_conflicts(repo)


@pytest.mark.parametrize(
    "remote_target_version", [None, "main", COOKIECUTTER_REMOTE_VERSION_2]
)
def test_update_passed_templates_to_newest_versions(
    remote_target_version: Optional[str],
    cookiecutter_one_template: CookiecutterTemplate,
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
        def get_sources_for_templates(
            self,
            templates: Sequence[Template],
            project_root: Path = Path("."),
            config: Optional[FlexlateConfig] = None,
        ) -> List[TemplateSource]:
            return [
                TemplateSource.from_template(
                    remote_template, target_version=remote_target_version
                ),
                TemplateSource.from_template(local_template),
            ]

    assert remote_template.version == COOKIECUTTER_REMOTE_VERSION_1
    assert local_template.version == COOKIECUTTER_ONE_VERSION
    updater.update_passed_templates_to_target_versions(
        [remote_template, local_template], config_manager=MockConfigManager()  # type: ignore
    )
    assert remote_template.version == COOKIECUTTER_REMOTE_VERSION_2
    assert local_template.version == "471c7dbeea2541fe9a7a558d3aafb6e0"


def test_update_passed_templates_to_newest_versions_but_already_at_targets(
    cookiecutter_one_template: CookiecutterTemplate,
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
        def get_sources_for_templates(
            self,
            templates: Sequence[Template],
            project_root: Path = Path("."),
            config: Optional[FlexlateConfig] = None,
        ) -> List[TemplateSource]:
            return [
                TemplateSource.from_template(
                    remote_template, target_version=COOKIECUTTER_REMOTE_VERSION_1
                ),
                TemplateSource.from_template(
                    # It is actually useless to put target version in a local template
                    # TODO: throw an error when user tries to target version for a local template
                    local_template,
                    target_version=COOKIECUTTER_ONE_VERSION,
                ),
            ]

    assert remote_template.version == COOKIECUTTER_REMOTE_VERSION_1
    assert local_template.version == COOKIECUTTER_ONE_VERSION
    updater.update_passed_templates_to_target_versions(
        [remote_template, local_template], config_manager=MockConfigManager()  # type: ignore
    )
    assert remote_template.version == COOKIECUTTER_REMOTE_VERSION_1
    # Local template is updated anyway, but it shows the old version due to target version
    assert local_template.version == COOKIECUTTER_ONE_VERSION


def _modify_cookiecutter_one_template_in_generated_folder(template: Template):
    template_folder = GENERATED_FILES_DIR / COOKIECUTTER_ONE_NAME
    shutil.copytree(template.path, template_folder, dirs_exist_ok=True)
    template.path = template_folder
    (template_folder / "some file.txt").touch()
