import pytest
from git import Repo

from flexlate.adder import Adder
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.update.main import Updater
from tests.config import GENERATED_FILES_DIR
from tests.fileutils import preprend_cookiecutter_one_generated_text

from tests.fixtures.git import *
from tests.fixtures.template import *


@pytest.fixture
def repo_with_cookiecutter_one_template_source(
    repo_with_placeholder_committed: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
) -> Repo:
    repo = repo_with_placeholder_committed
    adder = Adder()
    adder.add_template_source(
        cookiecutter_one_template,
        out_root=GENERATED_FILES_DIR,
        project_root=GENERATED_FILES_DIR,
    )
    stage_and_commit_all(repo, "Add cookiecutter one template source")
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_one(
    repo_with_placeholder_committed: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
) -> Repo:
    repo = repo_with_placeholder_committed
    updater = Updater()
    updater.update(repo, [cookiecutter_one_template], no_input=True)
    yield repo


@pytest.fixture
def repo_from_cookiecutter_one_with_modifications(
    repo_with_template_branch_from_cookiecutter_one: Repo,
) -> Repo:
    repo = repo_with_template_branch_from_cookiecutter_one
    preprend_cookiecutter_one_generated_text("hello\n")
    stage_and_commit_all(repo, "Prepend cookiecutter text with hello")
    yield repo
