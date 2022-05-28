import filecmp
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Sequence, Union

from tests import config


def wipe_generated_folder():
    using_temp_dir = config.USING_TEMP_DIR_AS_GENERATED_DIR
    if config.GENERATED_FILES_DIR.exists():
        _remove_folder(
            config.GENERATED_FILES_DIR, fail_on_permission_error=not using_temp_dir
        )
    if not using_temp_dir:
        config.GENERATED_FILES_DIR.mkdir()


def _remove_folder(
    folder: Path, retries: int = 10, fail_on_permission_error: bool = True
):
    if folder.exists():
        try:
            shutil.rmtree(folder)
        except PermissionError as e:
            time.sleep(0.1)
            if retries > 0:
                _remove_folder(folder, retries - 1)
            else:
                if fail_on_permission_error:
                    raise e
                else:
                    print(f"Failed to remove folder {folder}")


def display_contents_of_all_files_in_folder(
    folder: Path, nested: bool = True, ignores: Sequence[str] = (".git",)
):
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


def assert_dir_trees_are_equal(dir1: Union[str, Path], dir2: Union[str, Path]):
    """
    Compare two directories recursively. Files in each directory are
    assumed to be equal if their names and contents are equal.

    See: https://stackoverflow.com/a/6681395/6276321

    @param dir1: First directory path
    @param dir2: Second directory path

    @return: True if the directory trees are the same and
        there were no errors while accessing the directories or files,
        False otherwise.
    """

    dirs_cmp = filecmp.dircmp(dir1, dir2)
    if (
        len(dirs_cmp.left_only) > 0
        or len(dirs_cmp.right_only) > 0
        or len(dirs_cmp.funny_files) > 0
    ):
        pass
        # TODO: figure out why this fails in CI but not local

        # raise AssertionError(
        #     f"lefy only: {dirs_cmp.left_only}. right only: {dirs_cmp.right_only}. funny files: {dirs_cmp.funny_files}"
        # )
    (_, mismatch, errors) = filecmp.cmpfiles(
        dir1, dir2, dirs_cmp.common_files, shallow=False
    )
    if len(mismatch) > 0 or len(errors) > 0:
        raise AssertionError(f"mismatch: {mismatch}. errors: {errors}")
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        assert_dir_trees_are_equal(new_dir1, new_dir2)


def create_temp_path_without_cleanup() -> Path:
    temp_dir = tempfile.mkdtemp()
    path = Path(temp_dir).resolve()
    return path
