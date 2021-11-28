from pathlib import Path
from typing import List, Optional, Sequence, Dict, Any

from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field, validator, Extra

from flexlate.types import TemplateData


class TemplateSource(BaseModel):
    name: str
    path: str
    version: Optional[str] = None


class AppliedTemplateConfig(BaseModel):
    name: str
    data: TemplateData
    version: str
    root: Path = Path(".")


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
    def applied_templates_dict(self) -> Dict[str, AppliedTemplateConfig]:
        return {at.name: at for at in self.applied_templates}

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

    def update_applied_template(
        self, template_name: str, new_version: str, new_data: TemplateData
    ):
        _update_applied_template_for_config(self, template_name, new_version, new_data)
        for config in self.child_configs:
            _update_applied_template_for_config(
                config, template_name, new_version, new_data
            )

    class Config:
        extra = Extra.allow


def _update_applied_template_for_config(
    conf: FlexlateConfig, template_name: str, new_version: str, new_data: TemplateData
):
    for applied_template in conf.applied_templates:
        if applied_template.name == template_name:
            applied_template.version = new_version
            applied_template.data = new_data


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
