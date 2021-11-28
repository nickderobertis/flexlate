from pathlib import Path
from typing import Sequence, List

from flexlate.config import FlexlateConfig
from flexlate.template.base import Template
from flexlate.types import TemplateData


class ConfigManager:
    def load_config(self, project_root: Path = Path(".")) -> FlexlateConfig:
        return FlexlateConfig.from_dir_including_nested(project_root)

    def save_config(self, config: FlexlateConfig):
        config.save()

    def get_data_for_templates(
        self, templates: Sequence[Template], project_root: Path = Path(".")
    ) -> List[TemplateData]:
        return self.get_data_for_names(
            [template.name for template in templates], project_root=project_root
        )

    def get_data_for_names(
        self, names: Sequence[str], project_root: Path = Path(".")
    ) -> List[TemplateData]:
        config = self.load_config(project_root)
        applied_templates = config.applied_templates_dict
        data: List[TemplateData] = []
        for name in names:
            applied_template = applied_templates[name]
            data.append(applied_template.data)
        return data

    def update_applied_templates(
        self,
        templates: Sequence[Template],
        template_data: Sequence[TemplateData],
        project_root: Path = Path("."),
    ):
        config = self.load_config(project_root)
        if len(templates) != len(template_data):
            raise ValueError(
                f"length of templates and template data must match. got templates {templates} and data {template_data}"
            )
        for template, data in zip(templates, template_data):
            config.update_applied_template(template.name, template.version, data)
        self.save_config(config)
