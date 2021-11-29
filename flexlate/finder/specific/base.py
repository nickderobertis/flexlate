import abc
from pathlib import Path
from typing import Union, Protocol, TypeVar

from flexlate.template.base import Template
from flexlate.template_config.base import TemplateConfig

T = TypeVar("T", bound=Template)

class TemplateFinder(Protocol[T]):
    def find(self, path: Union[str, Path], **template_kwargs) -> T:
        ...

    def get_config(self, directory: Path) -> TemplateConfig:
        ...

    def matches_template_type(self, path: str) -> bool:
        ...
