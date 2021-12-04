from pathlib import Path
from typing import Union, Optional, Any, Dict

from cookiecutter.repository import is_repo_url
from git import Repo

from flexlate.ext_git import get_current_version


def get_version_from_source_path(
    path: Union[str, Path],
    local_path: Path,
    template_kwargs: Dict[str, Any],
) -> Optional[str]:
    if "version" in template_kwargs:
        return template_kwargs.pop("version")
    elif is_repo_url(str(path)):
        # Get version from repo
        return get_current_version(Repo(str(local_path)))


def get_git_url_from_source_path(
    path: Union[str, Path],
    template_kwargs: Dict[str, Any],
) -> Optional[str]:
    if "git_utl" in template_kwargs:
        return template_kwargs.pop("git_url")
    elif is_repo_url(str(path)):
        # Get version from repo
        return str(path)
