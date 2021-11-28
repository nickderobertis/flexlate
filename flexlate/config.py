from pathlib import Path
from typing import List, Optional, Sequence, Dict, Any, Protocol, Tuple

from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field, validator, Extra

from flexlate.exc import InvalidTemplateTypeException
from flexlate.finder.cookiecutter import CookiecutterFinder
from flexlate.template.base import Template
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData


# TODO: trying to be able to build template and data from config.
#  Need to be from applied templates, but sources have the template
#  types and paths needed to find them. Probably best to create
#  some combined config and put the logic to transform there
from flexlate.update.template import TemplateUpdate


class TemplateSource(BaseModel):
    name: str
    path: str
    type: TemplateType
    version: Optional[str] = None

    def to_template(self) -> Template:
        if self.type == TemplateType.BASE:
            raise InvalidTemplateTypeException("base type is not allowed for concrete templates")
        if self.type == TemplateType.COOKIECUTTER:
            finder = CookiecutterFinder()
        else:
            raise InvalidTemplateTypeException(f"no handling for template type {self.type} in creating template from source")
        kwargs = dict(name=self.name)
        if self.version is not None:
            kwargs.update(version=self.version)
        return finder.find(self.path, name=self.name, version=self.version)


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
    def from_dir_including_nested(cls, root: Path) -> "FlexlateConfig":
        file_name = cls._settings.config_file_name
        configs = _load_nested_configs(root, file_name, root)
        if not configs:
            return FlexlateConfig.load_or_create(root / file_name)
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
        obj._child_configs = configs
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
    root: Path, file_name: str, orig_root: Path
) -> List["FlexlateConfig"]:
    configs: List["FlexlateConfig"] = []
    path = root / file_name
    if path.exists():
        relative_path = root.relative_to(orig_root)
        config = FlexlateConfig.load(path)
        # Because we are combining configs, need to update the root for the applied templates
        for applied_template in config.applied_templates:
            applied_template.root = relative_path / applied_template.root
        configs.append(config)
    for folder_or_file in root.iterdir():
        if folder_or_file.is_dir():
            configs.extend(_load_nested_configs(folder_or_file, file_name, orig_root))
    return configs


if __name__ == "__main__":
    print(FlexlateConfig().to_json())
