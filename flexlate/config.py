from pathlib import Path
from typing import List, Optional, Sequence

from pyappconf import BaseConfig, AppConfig, ConfigFormats
from pydantic import BaseModel, Field, validator

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
    _settings = AppConfig(app_name="flexlate", default_format=ConfigFormats.JSON)

    @classmethod
    def from_dir_including_nested(cls, root: Path) -> "FlexlateConfig":
        file_name = cls._settings.config_file_name
        configs = _load_nested_configs(root, file_name, root)
        if not configs:
            FlexlateConfig.load_or_create(root / file_name)
        return cls.from_multiple(configs)

    @classmethod
    def from_multiple(cls, configs: Sequence["FlexlateConfig"]) -> "FlexlateConfig":
        template_sources: List[TemplateSource] = []
        applied_templates: List[AppliedTemplateConfig] = []
        for conf in configs:
            template_sources.extend(conf.template_sources)
            applied_templates.extend(conf.applied_templates)
        return cls(
            template_sources=template_sources, applied_templates=applied_templates
        )

    @validator("template_sources")
    def template_name_must_be_unique(cls, v):
        names = [template.name for template in v]
        unique_names = set(names)
        for name in unique_names:
            if names.count(name) > 1:
                raise ValueError(f"Must have unique name. Repeated: {name}")
        return v


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
