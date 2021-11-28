import os

import pytest

from tests.config import PROJECT_DIR
from tests.dirutils import wipe_generated_folder

@pytest.fixture(scope="session", autouse=True)
def before_all():
    # Fix for pycharm test runner that runs tests in tests folder
    os.chdir(PROJECT_DIR)
    yield

@pytest.fixture(scope="session", autouse=True)
def after_all():
    yield
    wipe_generated_folder()
