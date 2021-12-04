import os

import pytest

from tests.ciutils import is_running_on_ci
from tests.config import PROJECT_DIR
from tests.dirutils import wipe_generated_folder
from tests.gitutils import set_git_indentity_to_ci


@pytest.fixture(scope="session", autouse=True)
def before_all():
    # Fix for CI where git config is not set
    if is_running_on_ci():
        set_git_indentity_to_ci()

    # Fix for pycharm test runner that runs tests in tests folder
    os.chdir(PROJECT_DIR)
    yield

@pytest.fixture(scope="session", autouse=True)
def after_all():
    yield
    wipe_generated_folder()
