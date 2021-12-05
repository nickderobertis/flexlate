from pathlib import Path
from typing import List, Optional, Sequence, Dict, Any, Tuple, Union

from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field, validator, Extra

from flexlate.add_mode import AddMode
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import (
    InvalidTemplateTypeException,
    FlexlateProjectConfigFileNotExistsException,
)
from flexlate.finder.specific.cookiecutter import CookiecutterFinder
from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData


class TemplateSource(BaseModel):
    name: str
    path: str
    type: TemplateType
    version: Optional[str] = None
    target_version: Optional[str] = None
    git_url: Optional[str] = None

    @classmethod
    def from_template(
        cls, template: Template, target_version: Optional[str] = None
    ) -> "TemplateSource":
        return cls(
            name=template.name,
            path=str(template.path),
            version=template.version,
            type=template._type,
            target_version=target_version,
            git_url=template.git_url,
        )

    def to_template(self) -> Template:
        if self.type == TemplateType.BASE:
            raise InvalidTemplateTypeException(
                "base type is not allowed for concrete templates"
            )
        if self.type == TemplateType.COOKIECUTTER:
            finder = CookiecutterFinder()
        else:
            raise InvalidTemplateTypeException(
                f"no handling for template type {self.type} in creating template from source"
            )
        kwargs = dict(name=self.name)
        if self.version is not None:
            kwargs.update(version=self.version)
        if self.git_url is not None:
            kwargs.update(git_url=self.git_url)
        return finder.find(self.path, **kwargs)

    @property
    def update_location(self) -> Union[str, Path]:
        return self.git_url or self.path


class AppliedTemplateConfig(BaseModel):
    name: str
    data: TemplateData
    version: str
    root: Path = Path(".")


class AppliedTemplateWithSource(BaseModel):
    applied_template: AppliedTemplateConfig
    source: TemplateSource

    def to_template_and_data(self) -> Tuple[Template, TemplateData]:
        return self.source.to_template(), self.applied_template.data


class FlexlateConfig(BaseConfig):
    template_sources: List[TemplateSource] = Field(default_factory=list)
    applied_templates: List[AppliedTemplateConfig] = Field(default_factory=list)
    _child_configs: Optional[List["FlexlateConfig"]] = None
    _settings = AppConfig(
        app_name="flexlate", default_format=ConfigFormats.JSON, config_name="flexlate"
    )

    @classmethod
    def from_dir_including_nested(
        cls, root: Path, adjust_applied_paths: bool = True
    ) -> "FlexlateConfig":
        file_name = cls._settings.config_file_name
        configs = _load_nested_configs(
            root, file_name, root, adjust_applied_paths=adjust_applied_paths
        )
        if not configs:
            # Fall back to user config if it exists
            if cls._settings.config_location.exists():
                configs = [cls.load()]
        return cls.from_multiple(configs)

    @classmethod
    def from_multiple(cls, configs: Sequence["FlexlateConfig"]) -> "FlexlateConfig":
        template_sources: List[TemplateSource] = []
        applied_templates: List[AppliedTemplateConfig] = []
        for conf in configs:
            template_sources.extend(conf.template_sources)
            applied_templates.extend(conf.applied_templates)
        obj = cls(
            template_sources=template_sources, applied_templates=applied_templates
        )
        obj._child_configs = list(configs)
        return obj

    @validator("template_sources")
    def template_name_must_be_unique(cls, v):
        names = [template.name for template in v]
        unique_names = set(names)
        for name in unique_names:
            if names.count(name) > 1:
                raise ValueError(f"Must have unique name. Repeated: {name}")
        return v

    @property
    def template_sources_dict(self) -> Dict[str, TemplateSource]:
        return {ts.name: ts for ts in self.template_sources}

    @property
    def child_configs(self) -> List["FlexlateConfig"]:
        return self._child_configs or []

    def save(self, serializer_kwargs: Optional[Dict[str, Any]] = None, **kwargs):
        if not self.child_configs:
            # Normal singular config, fall back to py-app-conf behavior
            return super().save(serializer_kwargs, **kwargs)
        # Parent pseudo-config holding actual child configs, save those instead
        for config in self.child_configs:
            config.save(serializer_kwargs, **kwargs)

    class Config:
        extra = Extra.allow


def _load_nested_configs(
    root: Path, file_name: str, orig_root: Path, adjust_applied_paths: bool = True
) -> List["FlexlateConfig"]:
    configs: List["FlexlateConfig"] = []
    path = root / file_name
    if path.exists():
        relative_path = root.relative_to(orig_root)
        config = FlexlateConfig.load(path)
        # Because we are combining configs, need to update the root for the applied templates
        if adjust_applied_paths:
            for applied_template in config.applied_templates:
                applied_template.root = relative_path / applied_template.root
        configs.append(config)
    for folder_or_file in root.iterdir():
        if folder_or_file.is_dir():
            configs.extend(
                _load_nested_configs(
                    folder_or_file,
                    file_name,
                    orig_root,
                    adjust_applied_paths=adjust_applied_paths,
                )
            )
    return configs


class ProjectConfig(BaseModel):
    path: Path
    default_add_mode: AddMode = AddMode.LOCAL
    merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME
    template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME


class FlexlateProjectConfig(BaseConfig):
    projects: List[ProjectConfig] = Field(default_factory=list)
    _settings = AppConfig(
        app_name="flexlate",
        default_format=ConfigFormats.JSON,
        config_name="flexlate-project",
    )

    def get_project_for_path(self, path: Path = Path(".")) -> ProjectConfig:
        # Find the project root that is the closest parent to the given path
        project_closeness: List[Tuple[ProjectConfig, int]] = []
        for raw_project in self.projects:
            project = self._absolutify_project_config(raw_project)
            if project.path.absolute() == path.absolute():
                # If it is an exact match, just return it, we are done
                return project
            elif project.path.absolute() in path.absolute().parents:
                # Project path is a parent of the given path. Track the closeness
                # so that we can take the nearest parent
                project_closeness.append(
                    (project, path.absolute().parents.index(project.path.absolute()))
                )
            # Else, this path is totally unrelated, do nothing
        if len(project_closeness) == 0:
            raise FlexlateProjectConfigFileNotExistsException(
                f"could not find a project matching the path {path} from the "
                f"projects config file at {self.settings.config_location}"
            )

        # We have potentially multiple matching projects. Take the closest parent
        project_closeness.sort(key=lambda pc: pc[1])
        return project_closeness[0][0]

    def _absolutify_project_config(
        self, project_config: ProjectConfig
    ) -> ProjectConfig:
        if project_config.path.is_absolute():
            return project_config
        # Project config has a relative path, but that is relative to the config location,
        # not the current working directory
        real_path = self.settings.config_location.parent / project_config.path
        return ProjectConfig(
            path=real_path.absolute(), default_add_mode=project_config.default_add_mode
        )


if __name__ == "__main__":
    print(FlexlateConfig().to_json())
