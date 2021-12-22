import json
from pathlib import Path
from typing import Union, Optional, TypedDict, Dict, Tuple

from copier import vcs
from copier.config import make_config
from copier.config.factory import filter_config
from copier.config.user_data import load_config_data
from git import Repo

from flexlate.exc import CannotFindTemplateSourceException
from flexlate.ext_git import get_repo_remote_name_from_repo
from flexlate.finder.specific.base import TemplateFinder
from flexlate.finder.specific.git import (
    get_version_from_source_path,
    get_git_url_from_source_path,
)
from flexlate.template.copier import CopierTemplate
from flexlate.template_config.copier import CopierConfig
from flexlate.template_data import TemplateData


class CopierFinder(TemplateFinder[CopierTemplate]):
    def find(self, path: Union[str, Path], **template_kwargs) -> CopierTemplate:
        git_version: Optional[str] = None
        if "version" in template_kwargs:
            git_version = template_kwargs.pop("version")
        repo_path, name = _download_repo_if_necessary_get_local_path_and_name(
            path, version=git_version
        )
        config = self.get_config(repo_path)
        version = get_version_from_source_path(path, repo_path) or git_version
        git_url = get_git_url_from_source_path(path, template_kwargs)
        return CopierTemplate(
            config,
            repo_path,
            name=name,
            version=version,
            target_version=git_version,
            git_url=git_url,
        )

    def get_config(self, directory: Path) -> CopierConfig:
        raw_data = load_config_data(directory, quiet=True)
        defaults: QuestionsWithDefaults
        _, defaults = filter_config(raw_data)
        data: TemplateData = {}
        for key, value in defaults.items():
            if "default" in value:
                data[key] = value["default"]
            else:
                data[key] = None
        return CopierConfig(data)

    def matches_template_type(self, path: str) -> bool:
        try:
            repo_path, _ = _download_repo_if_necessary_get_local_path_and_name(path)
        except CannotFindTemplateSourceException:
            return False
        else:
            return (repo_path / "copier.yml").exists() or (
                repo_path / "copier.yaml"
            ).exists()


class DefaultData(TypedDict, total=False):
    default: str


QuestionsWithDefaults = Dict[str, DefaultData]


def _download_repo_if_necessary_get_local_path_and_name(
    path: Union[str, Path], version: Optional[str] = None
) -> Tuple[Path, str]:
    if isinstance(path, Path):
        return path, path.name

    repo = _get_repo_url_if_is_repo(path)
    if repo:
        src_path = vcs.clone(repo, version or "HEAD")
        repo = Repo(src_path)
        name = get_repo_remote_name_from_repo(repo)
        return Path(src_path), name

    raise CannotFindTemplateSourceException(
        f"Could not find template source {path} at version {version}"
    )


def _get_repo_url_if_is_repo(url: str) -> str:
    # Copier requires .git to be on the end of the url, add it if the user did not
    return vcs.get_repo(url) or vcs.get_repo(url + ".git")
