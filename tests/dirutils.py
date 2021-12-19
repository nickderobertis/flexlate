import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Sequence

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


def display_contents_of_all_files_in_folder(folder: Path, nested: bool = True, ignores: Sequence[str] = (".git",)):
    outer_divider = "================================================"
    divider = "--------------------------------------------------"
    for path in folder.absolute().iterdir():
        if path.name in ignores:
            continue
        if path.is_file():
            print(f"{outer_divider}\n{path}\n{divider}")
            try:
                print(path.read_text())
            except UnicodeDecodeError as e:
                print(f"FAILED TO READ TEXT WITH ERROR: {e}")
            print(f"{divider}\n{outer_divider}")
        elif path.is_dir():
            print(f"- {path} (directory)")
            if nested:
                display_contents_of_all_files_in_folder(path, nested)
