import os

import pytest

from tests.config import PROJECT_DIR
from tests.dirutils import wipe_generated_folder


@pytest.fixture(scope="function", autouse=True)
def before_each(monkeypatch):
    # Set git committer for generated repos during tests (necessary for CI)
    monkeypatch.setenv("GIT_AUTHOR_NAME", "flexlate-git")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "flexlate-git")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "flexlate-git@nickderobertis.com")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "flexlate-git@nickderobertis.com")


@pytest.fixture(scope="session", autouse=True)
def before_all():
    # Fix for pycharm test runner that runs tests in tests folder
    os.chdir(PROJECT_DIR)
    yield


@pytest.fixture(scope="session", autouse=True)
def after_all():
    yield
    wipe_generated_folder()
