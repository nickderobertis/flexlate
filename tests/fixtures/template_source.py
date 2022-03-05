import contextlib
import os.path
import shutil
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Final, Callable, Optional, ContextManager, Union

import pytest

from flexlate.add_mode import AddMode
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
    template_type: TemplateType
    input_data: TemplateData
    update_input_data: TemplateData
    version_1: str
    version_2: str
    is_local_template: bool = False
    version_migrate_func: Callable[[str], None] = lambda path: None
    render_relative_root_in_output: Path = Path(".")
    render_relative_root_in_template: Path = Path(".")
    expect_local_applied_template_path: Path = Path(".")
    evaluated_render_relative_root_in_output_creator: Callable[
        [TemplateData], Path
    ] = lambda data: Path(".")

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

    def relative(self, to: Path) -> "TemplateSourceFixture":
        new_fixture = deepcopy(self)
        if not self.is_local_template:
            # Nothing to do for remote templates as paths are urls
            return new_fixture
        new_fixture.path = os.path.relpath(self.path, to)
        return new_fixture

    @property
    def has_relative_path(self) -> bool:
        return self.is_local_template and not Path(self.path).is_absolute()

    @property
    def url_or_absolute_path(self) -> str:
        if not self.has_relative_path:
            return self.path
        # Must be local relative path. Paths are relative to GENERATED_REPO_DIR
        return str((GENERATED_REPO_DIR / Path(self.path)).resolve())

    def relative_path_relative_to(
        self, relative: Union[str, Path], orig_relative_to: Path = GENERATED_REPO_DIR
    ) -> str:
        if not self.has_relative_path:
            return self.path
        return os.path.relpath((orig_relative_to / self.path).resolve(), relative)


COOKIECUTTER_REMOTE_FIXTURE: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COOKIECUTTER_REMOTE_NAME,
    path=COOKIECUTTER_REMOTE_URL,
    type=TemplateSourceType.COOKIECUTTER_REMOTE,
    template_type=TemplateType.COOKIECUTTER,
    input_data=dict(name="woo", key="it works"),
    update_input_data=dict(name="updated", key="now"),
    version_1=COOKIECUTTER_REMOTE_VERSION_1,
    version_2=COOKIECUTTER_REMOTE_VERSION_2,
    render_relative_root_in_output=Path("{{ cookiecutter.name }}"),
    render_relative_root_in_template=Path("{{ cookiecutter.name }}"),
    evaluated_render_relative_root_in_output_creator=lambda data: Path(data["name"]),
    expect_local_applied_template_path=Path(".."),
)
COPIER_REMOTE_FIXTURE: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COPIER_REMOTE_NAME,
    path=COPIER_REMOTE_URL,
    type=TemplateSourceType.COPIER_REMOTE,
    template_type=TemplateType.COPIER,
    input_data=dict(question1="oh yeah", question2=10.5),
    update_input_data=dict(question1="please work", question2=2.8),
    version_1=COPIER_REMOTE_VERSION_1,
    version_2=COPIER_REMOTE_VERSION_2,
    render_relative_root_in_output=Path("."),
    render_relative_root_in_template=Path("output"),
)

cookiecutter_local_fixture: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COOKIECUTTER_ONE_NAME,
    path=str(COOKIECUTTER_ONE_DIR),
    type=TemplateSourceType.COOKIECUTTER_LOCAL,
    template_type=TemplateType.COOKIECUTTER,
    input_data=dict(a="z", c="f"),
    update_input_data=dict(a="n", c="q"),
    version_1=COOKIECUTTER_ONE_VERSION,
    version_2=COOKIECUTTER_ONE_MODIFIED_VERSION,
    is_local_template=True,
    version_migrate_func=modify_cookiecutter_one,
    render_relative_root_in_output=Path("{{ cookiecutter.a }}"),
    render_relative_root_in_template=Path("{{ cookiecutter.a }}"),
    evaluated_render_relative_root_in_output_creator=lambda data: Path(data["a"]),
    expect_local_applied_template_path=Path(".."),
)

COPIER_LOCAL_FIXTURE: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COPIER_ONE_NAME,
    path=str(COPIER_ONE_DIR),
    type=TemplateSourceType.COPIER_LOCAL,
    template_type=TemplateType.COPIER,
    input_data=dict(q1="abc", q2=2, q3="def"),
    update_input_data=dict(q1="qwe", q2=2, q3="rty"),
    version_1=COPIER_ONE_VERSION,
    version_2=COPIER_ONE_MODIFIED_VERSION,
    is_local_template=True,
    version_migrate_func=modify_copier_one,
)


local_absolute_path_fixtures: Final[List[TemplateSourceFixture]] = [
    cookiecutter_local_fixture,
    COPIER_LOCAL_FIXTURE,
]

remote_fixtures: Final[List[TemplateSourceFixture]] = [
    COOKIECUTTER_REMOTE_FIXTURE,
    COPIER_REMOTE_FIXTURE,
]

# Create relative path fixtures
local_relative_path_fixtures: Final[List[TemplateSourceFixture]] = [
    fixture.relative(GENERATED_REPO_DIR) for fixture in local_absolute_path_fixtures
]


all_standard_template_source_fixtures: Final[List[TemplateSourceFixture]] = [
    *remote_fixtures,
    *local_absolute_path_fixtures,
]


@contextlib.contextmanager
def template_source_with_temp_dir_if_local_template(
    template_source: TemplateSourceFixture,
) -> ContextManager[TemplateSourceFixture]:
    template_source = deepcopy(template_source)
    if template_source.is_local_template:
        path_is_relative = not Path(template_source.path).is_absolute()
        # Move into temporary directory so it can be updated locally
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir) / template_source.name
            source_path = template_source.path
            if path_is_relative:
                # Paths are set up to be relative to GENERATED_REPO_DIR
                # Convert into absolute path so it can be copied appropriately
                source_path = (GENERATED_REPO_DIR / source_path).resolve()
            shutil.copytree(source_path, template_dir)
            template_source.path = str(template_dir)
            if path_is_relative:
                # Original path was relative, need to make this path relative
                template_source = template_source.relative(GENERATED_REPO_DIR)
            yield template_source
    else:
        yield template_source


@pytest.fixture(scope="function", params=all_standard_template_source_fixtures)
def template_source(request) -> TemplateSourceFixture:
    with template_source_with_temp_dir_if_local_template(
        request.param
    ) as template_source:
        yield template_source


all_template_source_fixtures = [
    *all_standard_template_source_fixtures,
    *local_relative_path_fixtures,
]


@pytest.fixture(scope="function", params=all_template_source_fixtures)
def template_source_with_relative(request) -> TemplateSourceFixture:
    with template_source_with_temp_dir_if_local_template(
        request.param
    ) as template_source:
        yield template_source


one_remote_all_local_relative_fixtures = [
    COOKIECUTTER_REMOTE_FIXTURE,
    *local_relative_path_fixtures,
]


@pytest.fixture(scope="function", params=one_remote_all_local_relative_fixtures)
def template_source_one_remote_and_all_local_relative(request) -> TemplateSourceFixture:
    yield request.param


COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH = COOKIECUTTER_REMOTE_FIXTURE.path
