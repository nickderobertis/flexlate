import os
from pathlib import Path
from typing import List, Optional, Sequence, Dict, Any, Tuple, Union, cast

from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field, validator, Extra, PrivateAttr

from flexlate.add_mode import AddMode
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import (
    InvalidTemplateTypeException,
    FlexlateProjectConfigFileNotExistsException,
)
from flexlate.finder.specific.base import TemplateFinder
from flexlate.finder.specific.cookiecutter import CookiecutterFinder
from flexlate.finder.specific.copier import CopierFinder
from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData
from flexlate.template_path import get_local_repo_path_and_name_cloning_if_repo_url


class TemplateSource(BaseModel):
    name: str
    path: str
    type: TemplateType
    version: Optional[str] = None
    git_url: Optional[str] = None
    target_version: Optional[str] = None
    render_relative_root_in_output: Path = Path(".")
    render_relative_root_in_template: Path = Path(".")

    _config_file_location: Path = PrivateAttr()

    @classmethod
    def from_template(
        cls, template: Template, target_version: Optional[str] = None
    ) -> "TemplateSource":
        return cls(
            name=template.name,
            path=template.git_url
            if template.git_url is not None
            else str(template.path),
            version=template.version,
            type=template._type,
            target_version=target_version,
            git_url=template.git_url,
            render_relative_root_in_output=template.render_relative_root_in_output,
            render_relative_root_in_template=template.render_relative_root_in_template,
        )

    def to_template(self, version: Optional[str] = None) -> Template:
        if self.type == TemplateType.BASE:
            raise InvalidTemplateTypeException(
                "base type is not allowed for concrete templates"
            )
        finder: TemplateFinder
        if self.type == TemplateType.COOKIECUTTER:
            finder = CookiecutterFinder()
        elif self.type == TemplateType.COPIER:
            finder = CopierFinder()
        else:
            raise InvalidTemplateTypeException(
                f"no handling for template type {self.type} in creating template from source"
            )
        kwargs = dict(name=self.name)
        version = version or self.version
        if version is not None:
            kwargs.update(version=version)
        # TODO: Can we remove target_version from templates?
        if self.target_version is not None:
            kwargs.update(target_version=self.target_version)
        if self.git_url is not None:
            kwargs.update(git_url=self.git_url)
        local_path: Path
        if self.git_url is not None:
            # TODO: Avoid unnecessary git repo cloning
            #  We already know that we have it by this point, but need to get the local path
            #  and the logic to resolve the version that may be None is entertwined with the
            #  cloning and local path determination
            local_path, _ = get_local_repo_path_and_name_cloning_if_repo_url(
                self.git_url, version=version
            )
        else:
            local_path = self.absolute_local_path

        template = finder.find(self.git_url or str(local_path), local_path, **kwargs)
        # Keep original template source path (may be relative), so that later when
        # updating templates, it can update the path without forcing it to be absolute
        template.template_source_path = self.path
        return template

    @property
    def update_location(self) -> Union[str, Path]:
        return self.git_url or self.absolute_local_path

    @property
    def is_local_template(self) -> bool:
        return self.git_url is None

    @property
    def absolute_local_path(self) -> Path:
        if Path(self.path).is_absolute():
            return Path(self.path)
        else:
            # Convert to absolute path
            return (self._config_file_location.parent / Path(self.path)).resolve()


class AppliedTemplateConfig(BaseModel):
    name: str
    data: TemplateData
    version: str
    add_mode: AddMode
    root: Path = Path(".")

    _config_file_location: Path = PrivateAttr()
    _orig_root: Path = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Root may get updated externally during config loading when adjusting applied paths,
        # save the original root
        self._orig_root = self.root


class AppliedTemplateWithSource(BaseModel):
    applied_template: AppliedTemplateConfig
    source: TemplateSource

    def to_template_and_data(self) -> Tuple[Template, TemplateData]:
        return (
            self.source.to_template(version=self.applied_template.version),
            self.applied_template.data,
        )


class TemplateSourceWithTemplates(BaseModel):
    source: TemplateSource
    templates: List[Template]

    class Config:
        arbitrary_types_allowed = True


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
        # Add user config if it exists
        if cls._settings.config_location.exists():
            configs.append(cls.load())
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

    @property
    def empty(self) -> bool:
        return len(self.template_sources) == 0 and len(self.applied_templates) == 0

    @classmethod
    def load(cls, path: Optional[Union[str, Path]] = None) -> "FlexlateConfig":
        config = cast(FlexlateConfig, super().load(path))
        for template_source in config.template_sources:
            # Add location from which config was loaded so that later template source paths
            # can be made absolute before usage
            loaded_path = path or cls._settings.config_location
            template_source._config_file_location = Path(loaded_path)
        for applied_template in config.applied_templates:
            # Add location from which config was loaded so that it is easier to move
            # applied templates to correct location after updates
            loaded_path = path or cls._settings.config_location
            applied_template._config_file_location = Path(loaded_path)
        return config

    def save(self, serializer_kwargs: Optional[Dict[str, Any]] = None, **kwargs):
        if not self.child_configs:
            # Normal singular config, fall back to py-app-conf behavior
            return super().save(serializer_kwargs, **kwargs)
        # Parent pseudo-config holding actual child configs, save those instead
        for config in self.child_configs:
            if config.empty:
                # User must have removed all the sources and applied templates,
                # therefore we don't want the config file anymore
                if config.settings.config_location.exists():
                    os.remove(config.settings.config_location)
                continue

            # Normal case, non-empty config, save it
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
    remote: str = "origin"


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
