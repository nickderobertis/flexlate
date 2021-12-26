import abc
from pathlib import Path
from typing import Union, Protocol, TypeVar

from flexlate.template.base import Template
from flexlate.template_config.base import TemplateConfig

T = TypeVar("T", bound=Template)

# TODO: figure out how to type TemplateFinder properly
class TemplateFinder(Protocol[T]):  # type: ignore
    def find(self, path: str, local_path: Path, **template_kwargs) -> T:
        ...

    def get_config(self, directory: Path) -> TemplateConfig:
        ...

    def matches_template_type(self, path: Path) -> bool:
        ...
