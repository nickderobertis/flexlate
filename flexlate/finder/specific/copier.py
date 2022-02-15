from pathlib import Path
from typing import Optional, TypedDict, Dict

from copier.config.factory import filter_config
from copier.config.user_data import load_config_data

from flexlate.finder.specific.base import TemplateFinder
from flexlate.finder.specific.git import (
    get_version_from_source_path,
    get_git_url_from_source_path,
)
from flexlate.template.copier import CopierTemplate
from flexlate.template_config.copier import CopierConfig
from flexlate.template_data import TemplateData


class CopierFinder(TemplateFinder[CopierTemplate]):
    def find(self, path: str, local_path: Path, **template_kwargs) -> CopierTemplate:
        # TODO: determine why passing target_version through kwargs was not necessary for copier
        #  Had to do that for cookiecutter, but tests were passing without any changes here.
        git_version: Optional[str] = template_kwargs.get("version")
        custom_name: Optional[str] = template_kwargs.get("name")
        name = custom_name or local_path.name
        config = self.get_config(local_path)
        version = get_version_from_source_path(path, local_path) or git_version
        git_url = get_git_url_from_source_path(path, template_kwargs)
        template_source_path = git_url if git_url else path
        return CopierTemplate(
            config,
            local_path,
            name=name,
            version=version,
            target_version=git_version,
            git_url=git_url,
            template_source_path=template_source_path,
            render_relative_root_in_template=config.render_relative_root_in_template,
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
        render_relative_root_in_template: Path = Path(".")
        if "_subdirectory" in raw_data:
            render_relative_root_in_template = Path(raw_data["_subdirectory"])
        return CopierConfig(
            data, render_relative_root_in_template=render_relative_root_in_template
        )

    def matches_template_type(self, path: Path) -> bool:
        return (path / "copier.yml").exists() or (path / "copier.yaml").exists()


class DefaultData(TypedDict, total=False):
    default: str


QuestionsWithDefaults = Dict[str, DefaultData]
