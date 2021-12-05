import pytest
from git import Repo

from flexlate.adder import Adder
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.update.main import Updater
from tests.config import GENERATED_REPO_DIR
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
        repo,
        cookiecutter_one_template,
        out_root=GENERATED_REPO_DIR,
    )
    yield repo


@pytest.fixture
def repo_with_remote_cookiecutter_template_source(
    repo_with_placeholder_committed: Repo,
    cookiecutter_remote_template: CookiecutterTemplate,
) -> Repo:
    repo = repo_with_placeholder_committed
    adder = Adder()
    adder.add_template_source(
        repo,
        cookiecutter_remote_template,
        out_root=GENERATED_REPO_DIR,
    )
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_one(
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
) -> Repo:
    repo = repo_with_cookiecutter_one_template_source
    adder = Adder()
    adder.apply_template_and_add(
        repo, cookiecutter_one_template, out_root=GENERATED_REPO_DIR, no_input=True
    )
    yield repo


@pytest.fixture
def repo_from_cookiecutter_one_with_modifications(
    repo_with_template_branch_from_cookiecutter_one: Repo,
) -> Repo:
    repo = repo_with_template_branch_from_cookiecutter_one
    preprend_cookiecutter_one_generated_text("hello\n")
    stage_and_commit_all(repo, "Prepend cookiecutter text with hello")
    yield repo
