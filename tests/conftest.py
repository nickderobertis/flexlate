import os

import pytest

from flexlate import template_path
from tests.config import PROJECT_DIR, GENERATED_FILES_DIR
from tests.dirutils import wipe_generated_folder


@pytest.fixture(scope="function", autouse=True)
def before_each(monkeypatch):
    # Set git committer for generated repos during tests (necessary for CI)
    monkeypatch.setenv("GIT_AUTHOR_NAME", "flexlate-git")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "flexlate-git")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "flexlate-git@nickderobertis.com")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "flexlate-git@nickderobertis.com")
    # Fix for pycharm test runner that runs tests in tests folder
    os.chdir(PROJECT_DIR)
    # Save templates in generated folder rather than user dir
    monkeypatch.setattr(template_path, "CLONED_REPO_FOLDER", GENERATED_FILES_DIR)


@pytest.fixture(scope="function", autouse=True)
def after_each():
    yield
    wipe_generated_folder()
