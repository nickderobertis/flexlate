from pathlib import Path
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from flexlate.config import AppliedTemplateWithSource
from flexlate.template.base import Template
from flexlate.template_data import TemplateData

T = TypeVar("T", bound=Template)


class Renderable(BaseModel, Generic[T]):
    template: T
    data: TemplateData = Field(default_factory=dict)
    out_root: Path = Path(".")
    skip_prompts: bool = False

    @classmethod
    def from_applied_template_with_source(
        cls,
        applied_template_with_source: AppliedTemplateWithSource,
        data: Optional[TemplateData] = None,
    ) -> "Renderable":
        template, data_from_config = applied_template_with_source.to_template_and_data()
        all_data = {**data_from_config, **(data or {})}
        return cls(
            template=template,
            data=all_data,
            out_root=applied_template_with_source.applied_template.root,
        )

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, other):
        try:
            return all(
                [
                    # Assumed that templates have unique names by this point
                    # Comparing only name to avoid issues with comparing between temp repo and main repo, etc.
                    self.template.name == other.template.name,
                    self.data == other.data,
                    self.skip_prompts == other.skip_prompts,
                    # Resolve out root again for issues comparing between temp repo and main repo, etc.
                    # Put this last as it is the most expensive check
                    self.out_root.resolve() == other.out_root.resolve(),
                ]
            )
        except AttributeError:
            return False
