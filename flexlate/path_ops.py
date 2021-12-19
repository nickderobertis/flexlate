import os
import shutil
from pathlib import Path
from typing import Callable, Sequence


def make_func_that_creates_cwd_and_out_root_before_running(
    out_root: Path, func: Callable[[], None]
):
    """
    When switching branches, the CWD or target out_root may no longer exist.
    Pass a function to this function to create a function that
    creates those directories as needed before running the logic
    """
    cwd = Path(os.getcwd())
    absolute_out_root = out_root.absolute()

    def make_dirs_add_run_func():
        # Need to ensure that both cwd and out root exist on the template branch
        for p in [cwd, absolute_out_root]:
            if not p.exists():
                p.mkdir(parents=True)
        # If cwd was deleted when switching branches, need to navigate back there
        # or os.getcwd will throw a FileNotExistsError (which also breaks path.absolute())
        os.chdir(cwd)

        func()

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
