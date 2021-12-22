from dataclasses import dataclass
from typing import List, Final

import pytest

from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData
from tests.config import COOKIECUTTER_REMOTE_NAME, COOKIECUTTER_REMOTE_URL, COOKIECUTTER_REMOTE_VERSION_1, \
    COOKIECUTTER_REMOTE_VERSION_2


@dataclass
class TemplateSourceFixture:
    name: str
    path: str
    type: TemplateType
    input_data: TemplateData
    version_1: str
    version_2: str


all_template_source_fixtures: Final[List[TemplateSourceFixture]] = [
    TemplateSourceFixture(
        name=COOKIECUTTER_REMOTE_NAME,
        path=COOKIECUTTER_REMOTE_URL,
        type=TemplateType.COOKIECUTTER,
        input_data=dict(name="woo", key="it works"),
        version_1=COOKIECUTTER_REMOTE_VERSION_1,
        version_2=COOKIECUTTER_REMOTE_VERSION_2,
    )
]


@pytest.fixture(scope="module", params=all_template_source_fixtures)
def template_source(request) -> TemplateSourceFixture:
    return request.param
