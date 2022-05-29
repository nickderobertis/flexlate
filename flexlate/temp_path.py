import contextlib
import tempfile
from pathlib import Path
from typing import Iterator

from flexlate.constants import PY10


@contextlib.contextmanager
def create_temp_path() -> Iterator[Path]:
    """
    Returns a temporary folder path

    Use this instead of tempfile.TemporaryDirectory because:
    1. That returns a string and not a path
    2. On MacOS, the temp directory has a symlink. This resolves the symlink so that
       there won't be any mismatch in resolved paths.
    3. On Windows, the temp directory can fail to delete with a PermissionError. On Python
       3.10 and greater, there is a ignore_cleanup_errors parameter that can be added to
       tempfile.TemporaryDirectory to ignore the error. This function passes this
       parameter if we are running on Python 3.10 or greater.
    """
    kwargs = {}
    if PY10:
        kwargs["ignore_cleanup_errors"] = True
    with tempfile.TemporaryDirectory(**kwargs) as temp_dir:
        path = Path(temp_dir).resolve()
        yield path
