import os
import shutil
from contextlib import contextmanager
from pathlib import Path

from tests.config import GENERATED_FILES_DIR


def wipe_generated_folder():
    if GENERATED_FILES_DIR.exists():
        shutil.rmtree(GENERATED_FILES_DIR)
    GENERATED_FILES_DIR.mkdir()


@contextmanager
def change_directory_to(path: Path):
    current_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(current_path)
