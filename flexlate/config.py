import os
from pathlib import Path
from typing import (
    List,
    Optional,
    Sequence,
    Dict,
    Any,
    Tuple,
    Union,
    cast,
    Callable,
    Set,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from flexlate.update.template import TemplateUpdate

from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field, validator, Extra, PrivateAttr

from flexlate.add_mode import AddMode, get_expanded_out_root
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import (
    InvalidTemplateTypeException,
    FlexlateProjectConfigFileNotExistsException,
    FlexlateConfigFileNotExistsException,
    TemplateLookupException,
    CannotFindTemplateSourceException,
    CannotRemoveAppliedTemplateException,
    CannotRemoveTemplateSourceException,
)
from flexlate.finder.multi import MultiFinder
from flexlate.finder.specific.base import TemplateFinder
from flexlate.finder.specific.cookiecutter import CookiecutterFinder
from flexlate.finder.specific.copier import CopierFinder
from flexlate.path_ops import (
    location_relative_to_new_parent,
    make_absolute_path_from_possibly_relative_to_another_path,
)
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

    def to_template(
        self, version: Optional[str] = None, finder: MultiFinder = MultiFinder()
    ) -> Template:
        if self.type == TemplateType.BASE:
            raise InvalidTemplateTypeException(
                "base type is not allowed for concrete templates"
            )
        if version is None:
            version = self.version
        template = finder.find(
            self.git_url or str(self.absolute_local_path), version=version
        )
        template.name = self.name
        # TODO: Can we remove target_version from templates?
        template.target_version = self.target_version
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

    def get_applied_template_by_update(
        self, update: "TemplateUpdate"
    ) -> AppliedTemplateConfig:
        child_config = self._get_child_config_by_path(update.config_location)
        applied_template = child_config.applied_templates[update.index]
        if applied_template.name != update.template.name:
            raise TemplateLookupException(
                f"for index {update.index}, got applied template {applied_template} that does not match template {update.template}"
            )
        return applied_template

    def get_num_applied_templates_in_child_config(self, child_config_path: Path):
        child_config = self._get_child_config_by_path(child_config_path)
        return len(child_config.applied_templates)

    def update_applied_template(
        self,
        updater: Callable[[AppliedTemplateConfig], None],
        config_location: Path,
        index: int,
    ) -> None:
        # Do update in child config
        child_config = self._get_child_config_by_path(config_location)
        applied_template = child_config.applied_templates[index]
        updater(applied_template)
        # Do update in root config
        for at in self.applied_templates:
            if at == applied_template:
                updater(at)
                break

    def update_template_source(
        self,
        updater: Callable[[TemplateSource], None],
        name: str,
    ) -> None:
        # Do update in child config
        template_source: Optional[TemplateSource] = None
        for child_config in self.child_configs:
            for template_source in child_config.template_sources:
                if template_source.name == name:
                    updater(template_source)
                    break
        if template_source is None:
            raise CannotFindTemplateSourceException(f"template source {name} not found")
        # Do update in root config
        for ts in self.template_sources:
            if ts == template_source:
                updater(ts)
                break

    def update_template_sources(
        self,
        updater: Callable[[TemplateSource], None],
        names: Optional[Sequence[str]] = None,
    ) -> None:
        # Do update in child config
        matched_names: Set[str] = set()
        for child_config in self.child_configs:
            for template_source in child_config.template_sources:
                if names is None or template_source.name in names:
                    updater(template_source)
                    matched_names.add(template_source.name)
        if names is not None and len(matched_names) < len(names):
            diff = set(names) - matched_names
            raise CannotFindTemplateSourceException(
                f"template sources {diff} not found"
            )
        # Do update in root config
        for ts in self.template_sources:
            if names is None or ts.name in names:
                updater(ts)

    def add_template_source(
        self, template_source: TemplateSource, config_location: Path
    ) -> None:
        # Do update in child config
        child_config = self._get_or_create_child_config_by_path(config_location)
        child_config.template_sources.append(template_source)
        # Do update in root config
        self.template_sources.append(template_source)

    def remove_template_source(self, template_name: str, config_location: Path) -> None:
        # Do update in child config
        try:
            child_config = self._get_child_config_by_path(config_location)
        except FlexlateConfigFileNotExistsException as e:
            raise CannotRemoveTemplateSourceException(
                f"Cannot find any template source with name {template_name}"
            ) from e
        template_source: Optional[TemplateSource] = None
        for template_source in child_config.template_sources:
            if template_source.name == template_name:
                child_config.template_sources.remove(template_source)
                break
        if template_source is None:
            raise CannotFindTemplateSourceException(
                f"template source {template_name} not found in {config_location}"
            )
        # Do update in root config
        for ts in self.template_sources:
            if ts.name == template_source.name:
                self.template_sources.remove(ts)
                break

    def add_applied_template(
        self, applied_template: AppliedTemplateConfig, config_location: Path
    ) -> None:
        # Do update in child config
        child_config = self._get_or_create_child_config_by_path(config_location)
        child_config.applied_templates.append(applied_template)
        # Do update in root config
        self.applied_templates.append(applied_template)

    def remove_applied_template(
        self,
        template_name: str,
        config_location: Path,
        project_root: Path = Path("."),
        out_root: Path = Path("."),
        orig_project_root: Path = Path("."),
    ) -> None:
        # Do update in child config
        child_config = self._get_child_config_by_path(config_location)
        idx, applied_template = self._find_applied_template(
            template_name,
            config_location,
            project_root=project_root,
            out_root=out_root,
            orig_project_root=orig_project_root,
        )
        child_config.applied_templates.pop(idx)
        # Do update in root config
        for at in self.applied_templates:
            if at == applied_template:
                self.applied_templates.remove(at)
                break

    def move_applied_template(
        self,
        template_name: str,
        config_path: Path,
        new_config_path: Path,
        render_relative_root_in_output: Path,
        project_root: Path = Path("."),
        out_root: Path = Path("."),
        orig_project_root: Path = Path("."),
    ):
        child_config = self._get_or_create_child_config_by_path(config_path)
        template_index, _ = self._find_applied_template(
            template_name,
            config_path,
            project_root=project_root,
            out_root=out_root,
            orig_project_root=orig_project_root,
        )
        applied_template = child_config.applied_templates.pop(template_index)
        expanded_out_root = get_expanded_out_root(
            out_root,
            project_root,
            render_relative_root_in_output,
            applied_template.add_mode,
        )
        applied_template.root = expanded_out_root
        new_child_config = self._get_or_create_child_config_by_path(new_config_path)
        new_child_config.applied_templates.append(applied_template)
        # No need update to root config needed, because only location changed

    def move_template_source(
        self,
        template_name: str,
        config_path: Path,
        new_config_path: Path,
    ):
        child_config = self._get_or_create_child_config_by_path(config_path)
        template_index, _ = self._find_template_source(
            template_name,
            config_path,
        )
        template_source = child_config.template_sources.pop(template_index)
        if (
            template_source.is_local_template
            and not Path(template_source.path).is_absolute()
        ):
            abs_path = (config_path.parent / template_source.path).resolve()
            new_template_source_path = os.path.relpath(abs_path, new_config_path.parent)
        else:
            new_template_source_path = template_source.path
        template_source.path = new_template_source_path
        new_child_config = self._get_or_create_child_config_by_path(new_config_path)
        new_child_config.template_sources.append(template_source)
        # Update path for root config
        for ts in self.template_sources:
            if ts.name == template_source.name:
                ts.path = template_source.path
                break

    def _find_applied_template(
        self,
        template_name: str,
        config_path: Path,
        project_root: Path = Path("."),
        out_root: Path = Path("."),
        orig_project_root: Path = Path("."),
        adjust_applied_paths: bool = False,
    ) -> Tuple[int, AppliedTemplateConfig]:
        """

        :param template_name:
        :param config_path:
        :param project_root: The root of the current working project (may be a temp directory)
        :param out_root:
        :param orig_project_root: The root of the user's project (always stays the same, even
            when working in a temp directory)
        :return: index, applied template config tuple
        """
        child_config = self._get_or_create_child_config_by_path(config_path)
        template_index: Optional[int] = None
        orig_config_folder = location_relative_to_new_parent(
            child_config.settings.config_location.parent,
            project_root,
            orig_project_root,
        )
        absolute_out_root = make_absolute_path_from_possibly_relative_to_another_path(
            out_root, orig_config_folder
        )
        applied_template_reference_path = (
            orig_project_root if adjust_applied_paths else orig_config_folder
        )
        for i, applied_template in enumerate(child_config.applied_templates):

            absolute_template_out_root = (
                make_absolute_path_from_possibly_relative_to_another_path(
                    applied_template.root, applied_template_reference_path
                )
            )
            if (
                applied_template.name == template_name
                and absolute_template_out_root == absolute_out_root
            ):
                template_index = i
                break
        if template_index is None:
            raise CannotRemoveAppliedTemplateException(
                f"Cannot find any applied template with name {template_name} and root {out_root}"
            )
        applied_template = child_config.applied_templates[template_index]
        return template_index, applied_template

    def _find_template_source(
        self,
        template_name: str,
        config_path: Path,
    ) -> Tuple[int, TemplateSource]:
        """

        :param template_name:
        :param config_path:
        :param project_root: The root of the current working project (may be a temp directory)
        :param out_root:
        :param orig_project_root: The root of the user's project (always stays the same, even
            when working in a temp directory)
        :return: index, applied template config tuple
        """
        child_config = self._get_or_create_child_config_by_path(config_path)
        template_index: Optional[int] = None
        for i, template_source in enumerate(child_config.template_sources):
            if template_source.name == template_name:
                template_index = i
                break
        if template_index is None:
            raise CannotRemoveAppliedTemplateException(
                f"Cannot find any template source with name {template_name}"
            )
        template_source = child_config.template_sources[template_index]
        return template_index, template_source

    def _get_or_create_child_config_by_path(self, path: Path) -> "FlexlateConfig":
        try:
            return self._get_child_config_by_path(path)
        except FlexlateConfigFileNotExistsException:
            return self._create_child_config(path)

    def _create_child_config(self, config_path: Path) -> "FlexlateConfig":
        new_child = FlexlateConfig.load_or_create(config_path)
        if self._child_configs:
            self._child_configs.append(new_child)
        else:
            self._child_configs = [new_child]
        return new_child

    def _get_child_config_by_path(self, path: Path) -> "FlexlateConfig":
        for child_config in self.child_configs:
            if child_config.settings.config_location.absolute() == path.absolute():
                return child_config
        raise FlexlateConfigFileNotExistsException(
            f"could not find config with path {path}"
        )

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
            # Check to see if this is a nested flexlate project. If so, don't load the config,
            # instead that config should be associated with the nested project.
            if (folder_or_file / "flexlate-project.json").exists():
                continue

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
