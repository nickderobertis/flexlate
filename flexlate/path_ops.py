import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Sequence, Optional


def make_func_that_creates_cwd_and_out_root_before_running(
    out_root: Path, func: Callable[[Path], None]
):
    """
    When switching branches, the CWD or target out_root may no longer exist.
    Pass a function to this function to create a function that
    creates those directories as needed before running the logic
    """
    cwd = Path(os.getcwd())
    absolute_out_root = out_root.absolute()

    def make_dirs_add_run_func(path: Path):
        # Need to ensure that both cwd and out root exist on the template branch
        for p in [cwd, absolute_out_root]:
            if not p.exists():
                p.mkdir(parents=True)
        # If cwd was deleted when switching branches, need to navigate back there
        # or os.getcwd will throw a FileNotExistsError (which also breaks path.absolute())
        os.chdir(cwd)

        func(path)

    return make_dirs_add_run_func


def make_all_dirs(paths: Sequence[Path]):
    for path in paths:
        absolute_path = path.resolve()
        if not absolute_path.exists():
            absolute_path.mkdir(parents=True)


def copy_flexlate_configs(src: Path, dst: Path, root: Path):
    for path in src.absolute().iterdir():
        if path.name in ("flexlate.json", "flexlate-project.json"):
            shutil.copy(path, dst)
        elif path.name == ".git":
            continue
        elif path.is_dir():
            dst_dir = dst / path.name
            if not dst_dir.exists():
                dst_dir.mkdir()
            copy_flexlate_configs(path, dst_dir, root)


def location_relative_to_new_parent(
    path: Path,
    orig_parent: Path,
    new_parent: Path,
    path_is_relative_to: Optional[Path] = None,
) -> Path:
    if path_is_relative_to is None and not path.is_absolute():
        raise ValueError(
            f"must pass path_is_relative_to when passing relative path {path}"
        )
    abs_path: Path = path
    if not path.is_absolute() and path_is_relative_to is not None:
        abs_path = path_is_relative_to.absolute() / path
    try:
        result = new_parent / abs_path.relative_to(orig_parent)
        return result
    except ValueError as e:
        # python >= 3.9: is not in the subpath of
        # python <= 3.8: does not start with
        if "is not in the subpath of" in str(e) or "does not start with" in str(e):
            # Path is not in project, must be user path, return as is
            return path
        else:
            raise e


@contextmanager
def change_directory_to(path: Path):
    current_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(current_path)


def make_absolute_path_from_possibly_relative_to_another_path(
    path: Path, possibly_relative_to: Path
) -> Path:
    if path.is_absolute():
        return path
    else:
        return (possibly_relative_to / path).resolve()
