import json
import os.path
from pathlib import Path
from typing import Optional

from cookiecutter.find import find_template

from flexlate.finder.specific.base import TemplateFinder
from flexlate.finder.specific.git import (
    get_version_from_source_path,
    get_git_url_from_source_path,
)
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template_config.cookiecutter import CookiecutterConfig


class CookiecutterFinder(TemplateFinder[CookiecutterTemplate]):
    def find(
        self, path: str, local_path: Path, **template_kwargs
    ) -> CookiecutterTemplate:
        git_version: Optional[str] = None
        if "version" in template_kwargs:
            git_version = template_kwargs.pop("version")
        config = self.get_config(local_path)
        version = get_version_from_source_path(path, local_path) or git_version
        git_url = get_git_url_from_source_path(path, template_kwargs)
        template_source_path = git_url if git_url else path
        absolute_template_dir = find_template(local_path)
        relative_template_dir = Path(
            os.path.relpath(absolute_template_dir, local_path.resolve())
        )
        return CookiecutterTemplate(
            config,
            local_path,
            relative_template_dir,
            version=version,
            git_url=git_url,
            template_source_path=template_source_path,
            **template_kwargs
        )

    def get_config(self, directory: Path) -> CookiecutterConfig:
        config_path = directory / "cookiecutter.json"
        data = json.loads(config_path.read_text())
        return CookiecutterConfig(data)

    def matches_template_type(self, path: Path) -> bool:
        return (path / "cookiecutter.json").exists()
