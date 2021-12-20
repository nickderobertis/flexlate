import os
import shutil
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
        if not path.exists():
            path.mkdir(parents=True)


def copy_flexlate_configs(src: Path, dst: Path, root: Path):
    relative_path = src.absolute().relative_to(root.absolute())
    for path in src.absolute().iterdir():
        if path.name in ("flexlate.json", "flexlate-project.json"):
            shutil.copy(path, dst)
        elif path.name == ".git":
            continue
        elif path.is_dir():
            dst_dir = dst / relative_path / path.name
            if not dst_dir.exists():
                dst_dir.mkdir()
            copy_flexlate_configs(path, dst_dir, root)


def location_relative_to_new_parent(
    path: Path,
    orig_parent: Path,
    new_parent: Path,
    path_is_relative_to: Optional[Path] = None,
) -> Path:
    print("getting location relative to new parent")
    print("path", path)
    print("orig parent", orig_parent)
    print("new parent", new_parent)
    print("path is relative to", path_is_relative_to)
    if path_is_relative_to is None and not path.is_absolute():
        print("hit value error")
        raise ValueError(
            f"must pass path_is_relative_to when passing relative path {path}"
        )
    abs_path: Path = path
    if not path.is_absolute() and path_is_relative_to is not None:
        abs_path = path_is_relative_to.absolute() / path
    print("abs path is", abs_path)
    try:
        result = new_parent / abs_path.relative_to(orig_parent)
        print("got result", result)
        return result
    except ValueError as e:
        if "is not in the subpath of" in str(e):
            # Path is not in project, must be user path, return as is
            print("not in subpath, returning", path)
            return path
