import os

import pytest

from flexlate import template_path
from tests import config
from tests.dirutils import create_temp_path_without_cleanup, wipe_generated_folder

is_ci = os.getenv("CI", False)
use_temp_dir_as_generated_folder = is_ci


@pytest.fixture(scope="function", autouse=True)
def before_each(monkeypatch):
    # Set git committer for generated repos during tests (necessary for CI)
    monkeypatch.setenv("GIT_AUTHOR_NAME", "flexlate-git")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "flexlate-git")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "flexlate-git@nickderobertis.com")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "flexlate-git@nickderobertis.com")
    # Fix for pycharm test runner that runs tests in tests folder
    os.chdir(config.PROJECT_DIR)
    # If using temp dir as generated folder, overwrite the location
    if use_temp_dir_as_generated_folder:
        # Create the temp dir but don't cleanup, allow the OS to clean it up
        # Doing this because was hitting permission errors on Windows trying to clean
        # up generated test files
        temp_path = create_temp_path_without_cleanup()
        config.GENERATED_FILES_DIR = temp_path
        config.GENERATED_REPO_DIR = temp_path / "project"
        config.USING_TEMP_DIR_AS_GENERATED_DIR = True
    # Save templates in generated folder rather than user dir
    monkeypatch.setattr(template_path, "CLONED_REPO_FOLDER", config.GENERATED_FILES_DIR)


@pytest.fixture(scope="function", autouse=True)
def after_each():
    yield
    wipe_generated_folder()
