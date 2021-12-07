from pathlib import Path
from typing import TypeVar, Generic

from pydantic import BaseModel, Field

from flexlate.template.base import Template
from flexlate.template_data import TemplateData

T = TypeVar("T", bound=Template)


class Renderable(BaseModel, Generic[T]):
    template: T
    data: TemplateData = Field(default_factory=dict)
    out_root: Path = Path(".")

    class Config:
        arbitrary_types_allowed = True
