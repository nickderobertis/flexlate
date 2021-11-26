import abc
from pathlib import Path
from typing import Union

from flexlate.template.base import Template
from flexlate.template_config.base import TemplateConfig


class TemplateFinder(abc.ABC):
    def find(self, path: Union[str, Path]) -> Template:
        ...

    def get_config(self, directory: Path) -> TemplateConfig:
        ...
