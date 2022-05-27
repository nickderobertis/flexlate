import contextlib
import tempfile
from pathlib import Path
from typing import ContextManager


@contextlib.contextmanager
def create_temp_path() -> ContextManager[Path]:
    """
    Returns a temporary folder path

    Use this instead of tempfile.TemporaryDirectory because:
    1. That returns a string and not a path
    2. On MacOS, the temp directory has a symlink. This resolves the symlink so that
       there won't be any mismatch in resolved paths.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir).resolve()
        yield path
