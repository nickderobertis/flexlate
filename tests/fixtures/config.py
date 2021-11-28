import shutil

import pytest

from tests.config import CONFIGS_DIR, GENERATED_FILES_DIR
from tests.dirutils import wipe_generated_folder


@pytest.fixture
def generated_dir_with_configs():
    if GENERATED_FILES_DIR.exists():
        shutil.rmtree(GENERATED_FILES_DIR)
    shutil.copytree(CONFIGS_DIR, GENERATED_FILES_DIR)
    yield
    wipe_generated_folder()