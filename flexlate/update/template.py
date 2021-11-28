from copy import deepcopy
from pathlib import Path
from typing import Optional, Sequence, List

from pydantic import BaseModel

from flexlate.exc import InvalidTemplateDataException
from flexlate.template.base import Template
from flexlate.template_data import TemplateData


class TemplateUpdate(BaseModel):
    template: Template
    config_location: Path
    index: int
    data: Optional[TemplateData]

    class Config:
        arbitrary_types_allowed = True


def data_from_template_updates(updates: Sequence[TemplateUpdate]) -> List[TemplateData]:
    return [update.data or {} for update in updates]


def updates_with_updated_data(
    updates: Sequence[TemplateUpdate], data: Sequence[TemplateData]
) -> List[TemplateUpdate]:
    if len(updates) != len(data):
        raise InvalidTemplateDataException(
            f"should have equal length data {data} and updates {updates}"
        )
    out_updates: List[TemplateUpdate] = []
    for update, d in zip(updates, data):
        new_update = deepcopy(update)
        new_update.data = d
        out_updates.append(new_update)
    return out_updates
