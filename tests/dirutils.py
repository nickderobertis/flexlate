import shutil

from tests.config import GENERATED_FILES_DIR


def wipe_generated_folder():
    if GENERATED_FILES_DIR.exists():
        shutil.rmtree(GENERATED_FILES_DIR)
    GENERATED_FILES_DIR.mkdir()
