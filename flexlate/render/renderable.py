from pathlib import Path
from typing import TypeVar, Generic

from pydantic import BaseModel, Field

from flexlate.config import AppliedTemplateWithSource
from flexlate.template.base import Template
from flexlate.template_data import TemplateData

T = TypeVar("T", bound=Template)


class Renderable(BaseModel, Generic[T]):
    template: T
    data: TemplateData = Field(default_factory=dict)
    out_root: Path = Path(".")

    @classmethod
    def from_applied_template_with_source(
        cls, applied_template_with_source: AppliedTemplateWithSource
    ) -> "Renderable":
        template, data = applied_template_with_source.to_template_and_data()
        return cls(
            template=template,
            data=data,
            out_root=applied_template_with_source.applied_template.root,
        )

    class Config:
        arbitrary_types_allowed = True
