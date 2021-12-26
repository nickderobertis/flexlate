import pytest
from git import Repo

from flexlate.ext_git import stage_and_commit_all
from tests.config import GENERATED_REPO_DIR
from tests.dirutils import wipe_generated_folder
from flexlate.path_ops import change_directory_to
from tests.gitutils import (
    create_empty_repo,
    add_dummy_file_to_repo,
    add_dummy_file2_to_repo,
    add_gitignore_and_ignored_file_to_repo,
)


@pytest.fixture
def empty_generated_repo() -> Repo:
    wipe_generated_folder()
    yield create_empty_repo()


@pytest.fixture
def repo_with_placeholder_committed(empty_generated_repo: Repo) -> Repo:
    repo = empty_generated_repo
    with change_directory_to(GENERATED_REPO_DIR):
        add_dummy_file_to_repo(repo)
        stage_and_commit_all(repo, "Initial commit")
    yield repo


@pytest.fixture
def dirty_repo(repo_with_placeholder_committed: Repo) -> Repo:
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        add_dummy_file2_to_repo(repo)
    yield repo


@pytest.fixture
def repo_with_gitignore(repo_with_placeholder_committed: Repo) -> Repo:
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        add_gitignore_and_ignored_file_to_repo(repo)
        stage_and_commit_all(repo, "Add sample .gitignore with ignored file")
    yield repo
