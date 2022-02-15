import os.path
from copy import deepcopy
from pathlib import Path
from typing import Optional, Sequence, List

from pydantic import BaseModel

from flexlate.config import AppliedTemplateConfig, FlexlateConfig
from flexlate.exc import (
    InvalidTemplateDataException,
    CannotFindAppliedTemplateException,
)
from flexlate.path_ops import location_relative_to_new_parent
from flexlate.render.renderable import Renderable
from flexlate.template.base import Template
from flexlate.template_data import TemplateData


class TemplateUpdate(BaseModel):
    template: Template
    config_location: Path
    index: int
    data: Optional[TemplateData]

    class Config:
        arbitrary_types_allowed = True

    def to_applied_template(
        self, project_root: Path = Path("."), adjust_root: bool = True
    ) -> AppliedTemplateConfig:
        config = FlexlateConfig.load(self.config_location)
        applied_template = config.applied_templates[self.index]
        if applied_template.name != self.template.name:
            raise CannotFindAppliedTemplateException(
                f"could not find applied template for name {self.template.name} "
                f"and index {self.index} in config {self.config_location}"
            )
        # Update the data if it is supplied in the update
        if self.data:
            applied_template.data = self.data
        if adjust_root:
            # Because this config may not be at the project root, adjust the path as if it was
            absolute_orig_root = (
                applied_template.root
                if applied_template.root.is_absolute()
                else (
                    self.config_location.parent.resolve() / applied_template.root
                ).resolve()
            )
            new_root = Path(os.path.relpath(absolute_orig_root, project_root))
            applied_template.root = new_root
        return applied_template

    def to_renderable(
        self, project_root: Path = Path("."), adjust_root: bool = True
    ) -> Renderable[Template]:
        applied_template = self.to_applied_template(
            project_root=project_root, adjust_root=adjust_root
        )
        renderable: Renderable[Template] = Renderable(
            template=self.template,
            data=applied_template.data,
            out_root=applied_template.root,
        )
        return renderable

    def matches_renderable(
        self,
        renderable: Renderable,
        project_root: Path = Path("."),
        render_root: Path = Path("."),
        adjust_root: bool = True,
    ) -> bool:
        """
        Note: Does not check template data
        """
        self_renderable = self.to_renderable(
            project_root=project_root, adjust_root=adjust_root
        )
        self_renderable_out_root: Path = self_renderable.out_root
        if not self_renderable_out_root.is_absolute():
            self_renderable_out_root = (
                render_root / self_renderable_out_root
            ).resolve()
        renderable_out_root: Path = renderable.out_root.resolve()
        if not renderable_out_root.is_absolute():
            renderable_out_root = (render_root / renderable_out_root).resolve()
        return all(
            [
                self_renderable.template.name == renderable.template.name,
                self_renderable.template.version == renderable.template.version,
                self_renderable_out_root == renderable_out_root,
            ]
        )


def data_from_template_updates(updates: Sequence[TemplateUpdate]) -> List[TemplateData]:
    return [update.data or {} for update in updates]


def updates_with_updated_data(
    updates: Sequence[TemplateUpdate],
    data: Sequence[TemplateData],
    renderables: Sequence[Renderable],
    project_root: Path = Path("."),
    render_root: Path = Path("."),
    adjust_root: bool = True,
) -> List[TemplateUpdate]:
    if len(data) != len(renderables):
        raise InvalidTemplateDataException(
            f"should have equal length data {data} and renderables {renderables}"
        )
    out_updates: List[TemplateUpdate] = []
    for update in updates:
        new_update = deepcopy(update)
        # TODO: more efficient algorithm for matching rendered data with updates
        this_update_data: Optional[TemplateData] = None
        for i, renderable in enumerate(renderables):
            if update.matches_renderable(
                renderable,
                project_root=project_root,
                render_root=render_root,
                adjust_root=adjust_root,
            ):
                this_update_data = data[i]
                break
        if this_update_data is None:
            raise InvalidTemplateDataException(
                f"Could not find matching renderable for update {update} with "
                f"renderables {renderables}. Therefore data could not be matched"
            )
        new_update.data = this_update_data
        out_updates.append(new_update)
    return out_updates
