from pathlib import Path
from typing import Sequence, List, Optional, Tuple

from flexlate.config import (
    FlexlateConfig,
    TemplateSource,
    AppliedTemplateConfig,
    AppliedTemplateWithSource,
)
from flexlate.exc import (
    FlexlateConfigFileNotExistsException,
    TemplateLookupException,
    InvalidTemplateDataException,
)
from flexlate.template.base import Template
from flexlate.template_data import TemplateData, merge_data
from flexlate.update.template import TemplateUpdate, data_from_template_updates


class ConfigManager:
    def load_config(self, project_root: Path = Path(".")) -> FlexlateConfig:
        return FlexlateConfig.from_dir_including_nested(project_root)

    def save_config(self, config: FlexlateConfig):
        config.save()

    def get_applied_templates_with_sources(
        self, project_root: Path = Path("."), config: Optional[FlexlateConfig] = None
    ) -> List[AppliedTemplateWithSource]:
        config = config or self.load_config(project_root)
        sources = config.template_sources_dict
        applied_template_with_sources: List[AppliedTemplateWithSource] = []
        for applied_template in config.applied_templates:
            source = sources[applied_template.name]
            applied_template_with_sources.append(
                AppliedTemplateWithSource(
                    applied_template=applied_template, source=source
                )
            )
        return applied_template_with_sources

    def get_templates_with_data(
        self, project_root: Path = Path("."), config: Optional[FlexlateConfig] = None
    ) -> Tuple[List[Template], List[TemplateData]]:
        config = config or self.load_config(project_root)
        templates: List[Template] = []
        all_data: List[TemplateData] = []
        for applied_with_source in self.get_applied_templates_with_sources(
            project_root=project_root, config=config
        ):
            template, data = applied_with_source.to_template_and_data()
            templates.append(template)
            all_data.append(data)
        return templates, all_data

    def get_data_for_updates(
        self,
        updates: Sequence[TemplateUpdate],
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[TemplateData]:
        config = config or self.load_config(project_root)
        data: List[TemplateData] = []
        for update in updates:
            applied_template = _get_applied_template_from_config(config, update)
            data.append(applied_template.data)
        return data

    def get_no_op_updates(
        self,
        project_root: Path = Path("."),
        config: Optional[FlexlateConfig] = None,
    ) -> List[TemplateUpdate]:
        config = config or self.load_config(project_root)
        updates: List[TemplateUpdate] = []
        sources = config.template_sources_dict
        for child_config in config.child_configs:
            for i, applied_template in enumerate(child_config.applied_templates):
                source = sources[applied_template.name]
                template = source.to_template()
                template.version = applied_template.version
                updates.append(
                    TemplateUpdate(
                        template=template,
                        config_location=child_config.settings.config_location,
                        index=i,
                        data=applied_template.data,
                    )
                )
        return updates

    def update_templates(
        self,
        updates: Sequence[TemplateUpdate],
        project_root: Path = Path("."),
    ):
        config = self.load_config(project_root)
        existing_data = self.get_data_for_updates(updates, project_root, config)
        template_data = data_from_template_updates(updates)
        all_data = merge_data(template_data, existing_data)
        if len(updates) != len(all_data):
            raise InvalidTemplateDataException(
                f"length of templates and template data must match. got updates {updates} and data {template_data}"
            )
        for update, data in zip(updates, all_data):
            applied_template = _get_applied_template_from_config(config, update)
            applied_template.data = update.data or {}
            applied_template.version = update.template.version
            template_source = _get_template_source_from_config(config, update)
            template_source.version = update.template.version
            template_source.path = update.template.path
        self.save_config(config)

    def add_template_source(
        self, template: Template, config_path: Path, project_root: Path = Path(".")
    ):
        config = self.load_config(project_root=project_root)
        child_config = _get_or_create_child_config_by_path(config, config_path)
        source = TemplateSource(
            name=template.name,
            path=str(template.path),
            version=template.version,
            type=template._type,
        )
        child_config.template_sources.append(source)
        self.save_config(config)

    def add_applied_template(
        self,
        template: Template,
        config_path: Path,
        data: Optional[TemplateData] = None,
        project_root: Path = Path("."),
    ):
        config = self.load_config(project_root=project_root)
        child_config = _get_or_create_child_config_by_path(config, config_path)
        applied = AppliedTemplateConfig(
            name=template.name,
            data=data or {},
            version=template.version,
            root=config_path.parent,
        )
        child_config.applied_templates.append(applied)
        self.save_config(config)

    def get_num_applied_templates_in_child_config(
        self, child_config_path: Path, project_root: Path = Path(".")
    ):
        config = self.load_config(project_root)
        child_config = _get_child_config_by_path(config, child_config_path)
        return len(child_config.applied_templates)


def _get_child_config_by_path(config: FlexlateConfig, path: Path) -> FlexlateConfig:
    for child_config in config.child_configs:
        if child_config.settings.config_location == path:
            return child_config
    raise FlexlateConfigFileNotExistsException(
        f"could not find config with path {path}"
    )


def _get_or_create_child_config_by_path(
    config: FlexlateConfig, path: Path
) -> FlexlateConfig:
    try:
        return _get_child_config_by_path(config, path)
    except FlexlateConfigFileNotExistsException:
        return _create_child_config(config, path)


def _create_child_config(config: FlexlateConfig, config_path: Path) -> FlexlateConfig:
    new_child = FlexlateConfig.load_or_create(config_path)
    if config._child_configs:
        config._child_configs.append(new_child)
    else:
        config._child_configs = [new_child]
    return new_child


def _get_applied_template_from_config(
    config: FlexlateConfig, update: TemplateUpdate
) -> AppliedTemplateConfig:
    child_config = _get_child_config_by_path(config, update.config_location)
    applied_template = child_config.applied_templates[update.index]
    if applied_template.name != update.template.name:
        raise TemplateLookupException(
            f"for index {update.index}, got applied template {applied_template} that does not match template {update.template}"
        )
    return applied_template


def _get_template_source_from_config(
    config: FlexlateConfig, update: TemplateUpdate
) -> TemplateSource:
    for child_config in config.child_configs:
        sources = child_config.template_sources_dict
        if update.template.name in sources:
            return sources[update.template.name]
    raise TemplateLookupException(f"could not find source with name {update.template.name} in any child config")
