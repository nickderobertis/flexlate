import abc
from pathlib import Path
from typing import Optional, TypeVar, Type, Protocol

from flexlate.render.renderable import Renderable
from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData

T = TypeVar("T", bound=Template)


class SpecificTemplateRenderer(Protocol[T]):
    # Override these in subclass
    _template_cls: Type[T]
    _template_type: TemplateType = TemplateType.BASE

    def render(
        self,
        renderable: Renderable[T],
        no_input: bool = False,
    ) -> TemplateData:
        ...
