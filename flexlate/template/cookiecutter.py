from pathlib import Path

from flexlate.template.base import Template
from flexlate.template_config.cookiecutter import CookiecutterConfig


class CookiecutterTemplate(Template):

    def __init__(self, config: CookiecutterConfig, path: Path):
        super().__init__(config, path)