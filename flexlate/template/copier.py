from pathlib import Path
from typing import Optional

from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.template_config.copier import CopierConfig


class CopierTemplate(Template):
    _type = TemplateType.COPIER

    def __init__(
        self,
        config: CopierConfig,
        path: Path,
        name: Optional[str] = None,
        version: Optional[str] = None,
        target_version: Optional[str] = None,
        git_url: Optional[str] = None,
        template_source_path: Optional[str] = None,
        render_relative_root_in_template: Path = Path("."),
    ):
        super().__init__(
            config,
            path,
            name=name,
            version=version,
            target_version=target_version,
            git_url=git_url,
            template_source_path=template_source_path,
            render_relative_root_in_template=render_relative_root_in_template,
            # Render relative root in output is always . for Copier
            render_relative_root_in_output=Path("."),
        )
