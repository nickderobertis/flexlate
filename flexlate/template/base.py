import abc
from pathlib import Path

from flexlate.template.types import TemplateType
from flexlate.template_config.base import TemplateConfig


class Template(abc.ABC):
    # Override this in subclasses
    _type: TemplateType = TemplateType.BASE

    def __init__(self, config: TemplateConfig, path: Path):
        self.config = config
        self.path = path