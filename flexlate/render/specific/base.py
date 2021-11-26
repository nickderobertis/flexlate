import abc
from pathlib import Path
from typing import Optional

from flexlate.template.base import Template
from flexlate.template.types import TemplateType
from flexlate.types import TemplateData


class SpecificTemplateRenderer(abc.ABC):
    # Override this in subclass
    _template_type: TemplateType = TemplateType.BASE

    def render(
        self,
        template: Template,
        data: Optional[TemplateData] = None,
        out_path: Path = Path("."),
    ):
        ...
