import pytest
from git import Repo

from flexlate.ext_git import stage_and_commit_all
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.update.main import Updater
from tests.dirutils import wipe_generated_folder
from tests.fixtures.template import cookiecutter_one_template
from tests.gitutils import (
    create_empty_repo,
    add_dummy_file_to_repo,
    add_dummy_file2_to_repo,
)


@pytest.fixture
def empty_generated_repo() -> Repo:
    wipe_generated_folder()
    yield create_empty_repo()


@pytest.fixture
def repo_with_placeholder_committed(empty_generated_repo: Repo) -> Repo:
    repo = empty_generated_repo
    add_dummy_file_to_repo(repo)
    stage_and_commit_all(repo, "Initial commit")
    yield repo


@pytest.fixture
def dirty_repo(repo_with_placeholder_committed: Repo) -> Repo:
    repo = repo_with_placeholder_committed
    add_dummy_file2_to_repo(repo)
    yield repo


@pytest.fixture
def repo_with_template_branch_from_cookiecutter_one(
    repo_with_placeholder_committed: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
) -> Repo:
    repo = repo_with_placeholder_committed
    updater = Updater()
    updater.update(repo, [cookiecutter_one_template])
    yield repo
