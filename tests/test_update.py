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


# TODO: convert to add test. Should not be updating with no history
# def test_update_template_no_history(
#     cookiecutter_one_template: CookiecutterTemplate,
#     repo_with_placeholder_committed: Repo,
# ):
#     repo = repo_with_placeholder_committed
#     updater = Updater()
#     template_update = TemplateUpdate(template=cookiecutter_one_template, config_location=GENERATED_FILES_DIR / "flexlate.json", index=0)
#     updater.update(repo, [template_update], no_input=True)
#     main_branch: Head = repo.branches["master"]  # type: ignore
#     template_branch: Head = repo.branches[DEFAULT_BRANCH_NAME]  # type: ignore
#     assert repo.active_branch == main_branch
#     assert (
#         repo.commit().message
#         == "Update flexlate templates\n\none: d512c7e14e83cb4bc8d4e5ae06bb357e\n"
#     )
#     assert cookiecutter_one_generated_text_content() == ""
#     template_branch.checkout()
#     assert repo.active_branch == template_branch
#     assert cookiecutter_one_generated_text_content() == ""


def test_update_template_dirty_repo(
    cookiecutter_one_update_no_data: TemplateUpdate,
    dirty_repo: Repo,
):
    repo = dirty_repo
    updater = Updater()
    with pytest.raises(GitRepoDirtyException):
        updater.update(repo, [cookiecutter_one_update_no_data], no_input=True)

# TODO: fix tests after repo_with_template_branch_from_cookiecutter_one and repo_from_cookiecutter_one_with_modifications are fixed by using add
# def test_update_add_template(
#     cookiecutter_templates: List[CookiecutterTemplate],
#     repo_with_template_branch_from_cookiecutter_one: Repo,
# ):
#     repo = repo_with_template_branch_from_cookiecutter_one
#     updater = Updater()
#     updater.update(repo, cookiecutter_templates, no_input=True)
#     main_branch: Head = repo.branches["master"]  # type: ignore
#     template_branch: Head = repo.branches[DEFAULT_BRANCH_NAME]  # type: ignore
#     assert repo.active_branch == main_branch
#     assert (
#         repo.commit().message
#         == "Update flexlate templates\n\none: d512c7e14e83cb4bc8d4e5ae06bb357e\ntwo: ee5a0b0fd016835199ee7d3e0beb27cb\n"
#     )
#     assert cookiecutter_one_generated_text_content() == ""
#     assert cookiecutter_two_generated_text_content() == "e"
#     template_branch.checkout()
#     assert repo.active_branch == template_branch
#     assert cookiecutter_one_generated_text_content() == ""
#     assert cookiecutter_two_generated_text_content() == "e"


# def test_update_modify_template(
#     cookiecutter_one_modified_template: CookiecutterTemplate,
#     repo_with_template_branch_from_cookiecutter_one: Repo,
# ):
#     repo = repo_with_template_branch_from_cookiecutter_one
#     updater = Updater()
#     updater.update(repo, [cookiecutter_one_modified_template], no_input=True)
#     main_branch: Head = repo.branches["master"]  # type: ignore
#     template_branch: Head = repo.branches[DEFAULT_BRANCH_NAME]  # type: ignore
#     assert repo.active_branch == main_branch
#     assert (
#         repo.commit().message
#         == "Update flexlate templates\n\none: 7e18a6cc14856c8558ac999efa01e5e8\n"
#     )
#     assert cookiecutter_one_generated_text_content() == " and extra"
#     template_branch.checkout()
#     assert repo.active_branch == template_branch
#     assert cookiecutter_one_generated_text_content() == " and extra"
#
#
# def test_update_modify_template_conflict(
#     cookiecutter_one_modified_template: CookiecutterTemplate,
#     repo_from_cookiecutter_one_with_modifications: Repo,
# ):
#     repo = repo_from_cookiecutter_one_with_modifications
#     updater = Updater()
#     updater.update(repo, [cookiecutter_one_modified_template], no_input=True)
#     assert repo_has_merge_conflicts(repo)
