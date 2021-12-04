from pathlib import Path
from typing import Optional

from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.template_config.cookiecutter import CookiecutterConfig


class CookiecutterTemplate(Template):
    _type = TemplateType.COOKIECUTTER

    def __init__(
        self,
        config: CookiecutterConfig,
        path: Path,
        name: Optional[str] = None,
        version: Optional[str] = None,
        target_version: Optional[str] = None,
        git_url: Optional[str] = None,
    ):
        super().__init__(
            config,
            path,
            name=name,
            version=version,
            target_version=target_version,
            git_url=git_url,
        )
