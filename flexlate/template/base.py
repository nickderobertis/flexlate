import abc
from pathlib import Path
from typing import Optional

from flexlate.template.types import TemplateType
from flexlate.template_config.base import TemplateConfig


class Template(abc.ABC):
    # Override this in subclasses
    _type: TemplateType = TemplateType.BASE

    def __init__(self, config: TemplateConfig, path: Path, name: Optional[str] = None):
        self.config = config
        self.path = path
        self.name = name or self.default_name

    @property
    def default_name(self) -> str:
        return self.path.name