import shutil

import pytest

from tests import config, gen_configs
from tests.dirutils import wipe_generated_folder


@pytest.fixture
def generated_dir_with_configs():
    gen_configs.main(config.GENERATED_FILES_DIR, config.GENERATED_FILES_DIR)
    yield
