import abc
from pathlib import Path
from typing import Optional, TypeVar, Type, Protocol

from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.types import TemplateData

T = TypeVar("T", bound=Template)


class SpecificTemplateRenderer(Protocol[T]):
    # Override these in subclass
    _template_cls: Type[T]
    _template_type: TemplateType = TemplateType.BASE

    def render(
        self,
        template: T,
        data: Optional[TemplateData] = None,
        out_path: Path = Path("."),
        no_input: bool = False,
    ):
        ...
