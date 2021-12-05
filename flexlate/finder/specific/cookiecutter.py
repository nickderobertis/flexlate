import json
from pathlib import Path
from typing import Union, Optional

from cookiecutter.config import get_user_config
from cookiecutter.repository import determine_repo_dir, is_repo_url
from git import Repo

from flexlate.ext_git import get_current_version
from flexlate.finder.specific.base import TemplateFinder
from flexlate.finder.specific.git import (
    get_version_from_source_path,
    get_git_url_from_source_path,
)
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template_config.cookiecutter import CookiecutterConfig


class CookiecutterFinder(TemplateFinder[CookiecutterTemplate]):
    def find(self, path: Union[str, Path], **template_kwargs) -> CookiecutterTemplate:
        git_version: Optional[str] = None
        if "version" in template_kwargs:
            git_version = template_kwargs.pop("version")
        repo_path = _download_repo_if_necessary_get_local_path(
            path, checkout=git_version
        )
        config = self.get_config(repo_path)
        version = get_version_from_source_path(path, repo_path) or git_version
        git_url = get_git_url_from_source_path(path, template_kwargs)
        return CookiecutterTemplate(
            config,
            repo_path,
            version=version,
            target_version=git_version,
            git_url=git_url,
            **template_kwargs
        )

    def get_config(self, directory: Path) -> CookiecutterConfig:
        config_path = directory / "cookiecutter.json"
        data = json.loads(config_path.read_text())
        return CookiecutterConfig(data)

    def matches_template_type(self, path: str) -> bool:
        repo_path = _download_repo_if_necessary_get_local_path(path)
        return (repo_path / "cookiecutter.json").exists()


def _download_repo_if_necessary_get_local_path(
    path: Union[str, Path], checkout: Optional[str] = None
) -> Path:
    config_dict = get_user_config()
    repo_dir, _ = determine_repo_dir(
        template=str(path),
        abbreviations=config_dict["abbreviations"],
        clone_to_dir=config_dict["cookiecutters_dir"],
        checkout=checkout,
        no_input=True,
    )
    return Path(repo_dir)
