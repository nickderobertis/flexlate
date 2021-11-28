import shutil
import tempfile
from pathlib import Path

import pytest
from git import Repo, Head

from flexlate.exc import GitRepoDirtyException
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.ext_git import DEFAULT_BRANCH_NAME
from flexlate.update.main import Updater
from flexlate.update.template import TemplateUpdate
from tests.config import GENERATED_FILES_DIR
from tests.fileutils import (
    cookiecutter_one_generated_text_content,
    cookiecutter_two_generated_text_content,
)
from tests.fixtures.git import *
from tests.fixtures.template import *
from tests.fixtures.templated_repo import *
from tests.fixtures.updates import *
from tests.gitutils import repo_has_merge_conflicts

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
    repo_with_template_branch_from_cookiecutter_one: Repo,
):
    repo = repo_with_template_branch_from_cookiecutter_one
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template], project_root=GENERATED_FILES_DIR
    )
    updater.update(repo, template_updates, no_input=True)
    main_branch: Head = repo.branches["master"]  # type: ignore
    template_branch: Head = repo.branches[DEFAULT_BRANCH_NAME]  # type: ignore
    assert repo.active_branch == main_branch
    assert (
        repo.commit().message
        == "Update flexlate templates\n\none: 7e18a6cc14856c8558ac999efa01e5e8\n"
    )
    assert cookiecutter_one_generated_text_content() == " and extra"
    template_branch.checkout()
    assert repo.active_branch == template_branch
    assert cookiecutter_one_generated_text_content() == " and extra"


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
