from pathlib import Path
from typing import Union, Optional, Any, Dict

from git import Repo

from flexlate.ext_git import get_current_version
from flexlate.template_path import is_repo_url


def get_version_from_source_path(
    path: Union[str, Path],
    local_path: Path,
) -> Optional[str]:
    if is_repo_url(str(path)):
        # Get version from repo
        return get_current_version(Repo(str(local_path)))
    return None


def get_git_url_from_source_path(
    path: Union[str, Path],
    template_kwargs: Dict[str, Any],
) -> Optional[str]:
    if "git_url" in template_kwargs:
        potential_url = template_kwargs.pop("git_url")
        if potential_url:
            return potential_url
    if is_repo_url(str(path)):
        # Get version from repo
        return str(path)
    return None
