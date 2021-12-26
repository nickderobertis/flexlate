import re
from pathlib import Path

import appdirs

from flexlate.exc import InvalidTemplatePathException
from flexlate.ext_git import clone_repo

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


def get_local_repo_path_cloning_if_repo_url(
    path: str, dst_folder: Path = CLONED_REPO_FOLDER
) -> Path:
    if is_local_template(path):
        return Path(path)

    if not is_repo_url(path):
        raise InvalidTemplatePathException(
            f"Template path {path} is not a valid local path or remote url"
        )

    # Must be a repo url, clone it and return the cloned path
    repo = clone_repo(path, dst_folder)
    # For type narrowing
    if repo.working_dir is None:
        raise ValueError("repo working dir cannot be None")
    return Path(repo.working_dir)
