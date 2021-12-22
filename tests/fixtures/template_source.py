from dataclasses import dataclass
from enum import Enum
from typing import List, Final

import pytest

from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData
from tests.config import (
    COOKIECUTTER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_VERSION_1,
    COOKIECUTTER_REMOTE_VERSION_2,
    COPIER_REMOTE_NAME,
    COPIER_REMOTE_URL,
    COPIER_REMOTE_VERSION_1,
    COPIER_REMOTE_VERSION_2,
)


class TemplateSourceType(str, Enum):
    COOKIECUTTER_REMOTE = "cookiecutter_remote"
    COPIER_REMOTE = "copier_remote"


@dataclass
class TemplateSourceFixture:
    name: str
    path: str
    type: TemplateSourceType
    input_data: TemplateData
    version_1: str
    version_2: str


all_template_source_fixtures: Final[List[TemplateSourceFixture]] = [
    TemplateSourceFixture(
        name=COOKIECUTTER_REMOTE_NAME,
        path=COOKIECUTTER_REMOTE_URL,
        type=TemplateSourceType.COOKIECUTTER_REMOTE,
        input_data=dict(name="woo", key="it works"),
        version_1=COOKIECUTTER_REMOTE_VERSION_1,
        version_2=COOKIECUTTER_REMOTE_VERSION_2,
    ),
    TemplateSourceFixture(
        name=COPIER_REMOTE_NAME,
        path=COPIER_REMOTE_URL,
        type=TemplateSourceType.COPIER_REMOTE,
        input_data=dict(question1="oh yeah", question2=10.5),
        version_1=COPIER_REMOTE_VERSION_1,
        version_2=COPIER_REMOTE_VERSION_2,
    ),
]


@pytest.fixture(scope="module", params=all_template_source_fixtures)
def template_source(request) -> TemplateSourceFixture:
    return request.param
