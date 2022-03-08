import re
from pathlib import Path
from typing import Optional, Tuple

import appdirs

from flexlate.exc import InvalidTemplatePathException
from flexlate.ext_git import clone_repo_at_version_get_repo_and_name, checkout_version

CLONED_REPO_FOLDER = Path(appdirs.user_data_dir("flexlate"))

REPO_REGEX = re.compile(
    r"""
# something like git:// ssh:// file:// etc.
((((git|hg)\+)?(git|ssh|file|https?):(//)?)
 |                                      # or
 (\w+@[\w.]+)                          # something like user@...
)
""",
    re.VERBOSE,
)


def is_repo_url(value):
    """Return True if value is a repository URL."""
    return bool(REPO_REGEX.match(value))


def is_local_template(path: str) -> bool:
    return Path(path).exists()


def get_local_repo_path_and_name_cloning_if_repo_url(
    path: str, version: Optional[str] = None, dst_folder: Optional[Path] = None
) -> Tuple[Path, str]:
    if dst_folder is None:
        # Setting here rather than in default params so that mocking
        # during tests is possible
        dst_folder = CLONED_REPO_FOLDER

    if is_local_template(path):
        local_path = Path(path)
        return local_path, local_path.resolve().name

    if not is_repo_url(path):
        raise InvalidTemplatePathException(
            f"Template path {path} is not a valid local path or remote url"
        )

    # Must be a repo url, clone it and return the cloned path
    repo, name = clone_repo_at_version_get_repo_and_name(
        path, dst_folder, version=version
    )

    # For type narrowing
    if repo.working_dir is None:
        raise ValueError("repo working dir cannot be None")
    return Path(repo.working_dir), name
