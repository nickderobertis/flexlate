import shutil

import pytest

from tests import config
from tests.dirutils import wipe_generated_folder


@pytest.fixture
def generated_dir_with_configs():
    if config.GENERATED_FILES_DIR.exists():
        shutil.rmtree(config.GENERATED_FILES_DIR)
    shutil.copytree(config.CONFIGS_DIR, config.GENERATED_FILES_DIR)
    yield
    wipe_generated_folder()
