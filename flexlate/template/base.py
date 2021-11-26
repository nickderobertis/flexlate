import abc
from pathlib import Path

from flexlate.template_config.base import TemplateConfig


class Template(abc.ABC):

    def __init__(self, config: TemplateConfig, path: Path):
        self.config = config
        self.path = path