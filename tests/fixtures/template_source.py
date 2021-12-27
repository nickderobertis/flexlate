import os.path
import shutil
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Final, Callable, Optional

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
    COOKIECUTTER_ONE_NAME,
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_ONE_VERSION,
    COOKIECUTTER_ONE_MODIFIED_VERSION,
    COPIER_ONE_NAME,
    COPIER_ONE_DIR,
    COPIER_ONE_VERSION,
    COPIER_ONE_MODIFIED_VERSION,
    GENERATED_REPO_DIR,
    GENERATED_FILES_DIR,
)
from tests.fixtures.template import modify_cookiecutter_one, modify_copier_one


class TemplateSourceType(str, Enum):
    COOKIECUTTER_REMOTE = "cookiecutter_remote"
    COPIER_REMOTE = "copier_remote"
    COOKIECUTTER_LOCAL = "cookiecutter_local"
    COPIER_LOCAL = "copier_local"


@dataclass
class TemplateSourceFixture:
    name: str
    path: str
    type: TemplateSourceType
    input_data: TemplateData
    version_1: str
    version_2: str
    is_local_template: bool = False
    version_migrate_func: Callable[[str], None] = lambda path: None

    @property
    def default_version(self) -> str:
        if self.is_local_template:
            # Local templates are not modified by default and so will get version 1
            return self.version_1
        # Remote templates are at the latest version already
        return self.version_2

    @property
    def url(self) -> Optional[str]:
        if self.is_local_template:
            return None
        return self.path

    def expect_path(self, version: Optional[str] = None) -> str:
        version = version or self.default_version
        if self.is_local_template:
            return self.path
        # appdirs user data directory is mocked to GENERATED_FILES_DIR in tests
        return str(GENERATED_FILES_DIR / self.name / version)

    def relative(self, to: Path) -> "TemplateSourceFixture":
        new_fixture = deepcopy(self)
        if not self.is_local_template:
            # Nothing to do for remote templates as paths are urls
            return new_fixture
        new_fixture.path = os.path.relpath(self.path, to)
        return new_fixture


cookiecutter_remote_fixture: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COOKIECUTTER_REMOTE_NAME,
    path=COOKIECUTTER_REMOTE_URL,
    type=TemplateSourceType.COOKIECUTTER_REMOTE,
    input_data=dict(name="woo", key="it works"),
    version_1=COOKIECUTTER_REMOTE_VERSION_1,
    version_2=COOKIECUTTER_REMOTE_VERSION_2,
)
copier_remote_fixture: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COPIER_REMOTE_NAME,
    path=COPIER_REMOTE_URL,
    type=TemplateSourceType.COPIER_REMOTE,
    input_data=dict(question1="oh yeah", question2=10.5),
    version_1=COPIER_REMOTE_VERSION_1,
    version_2=COPIER_REMOTE_VERSION_2,
)

cookiecutter_local_fixture: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COOKIECUTTER_ONE_NAME,
    path=COOKIECUTTER_ONE_DIR,
    type=TemplateSourceType.COOKIECUTTER_LOCAL,
    input_data=dict(a="z", c="f"),
    version_1=COOKIECUTTER_ONE_VERSION,
    version_2=COOKIECUTTER_ONE_MODIFIED_VERSION,
    is_local_template=True,
    version_migrate_func=modify_cookiecutter_one,
)

copier_local_fixture: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COPIER_ONE_NAME,
    path=COPIER_ONE_DIR,
    type=TemplateSourceType.COPIER_LOCAL,
    input_data=dict(q1="abc", q2=2, q3="def"),
    version_1=COPIER_ONE_VERSION,
    version_2=COPIER_ONE_MODIFIED_VERSION,
    is_local_template=True,
    version_migrate_func=modify_copier_one,
)


local_absolute_path_fixtures: Final[List[TemplateSourceFixture]] = [
    cookiecutter_local_fixture,
    copier_local_fixture,
]

remote_fixtures: Final[List[TemplateSourceFixture]] = [
    cookiecutter_remote_fixture,
    copier_remote_fixture,
]

# Create relative path fixtures
local_relative_path_fixtures: Final[List[TemplateSourceFixture]] = [
    fixture.relative(GENERATED_REPO_DIR) for fixture in local_absolute_path_fixtures
]


all_standard_template_source_fixtures: Final[List[TemplateSourceFixture]] = [
    *remote_fixtures,
    *local_absolute_path_fixtures,
]


@pytest.fixture(scope="function", params=all_standard_template_source_fixtures)
def template_source(request) -> TemplateSourceFixture:
    template_source: TemplateSourceFixture = deepcopy(request.param)
    if template_source.is_local_template:
        # Move into temporary directory so it can be updated locally
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir) / template_source.name
            shutil.copytree(template_source.path, template_dir)
            template_source.path = str(template_dir)
            yield template_source
    else:
        yield template_source


one_remote_all_local_relative_fixtures = [
    cookiecutter_remote_fixture,
    *local_relative_path_fixtures,
]


@pytest.fixture(scope="function", params=one_remote_all_local_relative_fixtures)
def template_source_one_remote_and_all_local_relative(request) -> TemplateSourceFixture:
    yield request.param


COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH = cookiecutter_remote_fixture.expect_path()
