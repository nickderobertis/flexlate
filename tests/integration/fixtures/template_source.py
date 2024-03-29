import contextlib
import os.path
import shutil
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from subprocess import CompletedProcess
from typing import Callable, ContextManager, Final, List, Optional, Union

import pytest

from flexlate.add_mode import AddMode
from flexlate.path_ops import change_directory_to
from flexlate.temp_path import create_temp_path
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData
from tests import config
from tests.config import (
    COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_NAME,
    COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_URL,
    COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_VERSION_1,
    COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_VERSION_2,
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_ONE_MODIFIED_VERSION,
    COOKIECUTTER_ONE_NAME,
    COOKIECUTTER_ONE_VERSION,
    COOKIECUTTER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_VERSION_1,
    COOKIECUTTER_REMOTE_VERSION_2,
    COOKIECUTTER_WITH_HOOKS_DIR,
    COOKIECUTTER_WITH_HOOKS_MODIFIED_VERSION,
    COOKIECUTTER_WITH_HOOKS_NAME,
    COOKIECUTTER_WITH_HOOKS_VERSION,
    COPIER_FROM_COOKIECUTTER_ONE_VERSION,
    COPIER_ONE_DIR,
    COPIER_ONE_MODIFIED_VERSION,
    COPIER_ONE_NAME,
    COPIER_ONE_VERSION,
    COPIER_REMOTE_NAME,
    COPIER_REMOTE_URL,
    COPIER_REMOTE_VERSION_1,
    COPIER_REMOTE_VERSION_2,
    COPIER_WITH_TASKS_DIR,
    COPIER_WITH_TASKS_MODIFIED_VERSION,
    COPIER_WITH_TASKS_NAME,
    COPIER_WITH_TASKS_VERSION,
)
from tests.dirutils import remove_folder
from tests.ext_subprocess import run
from tests.fixtures.template import (
    modify_cookiecutter_one,
    modify_cookiecutter_one_to_be_copier,
    modify_copier_one,
    modify_copier_with_tasks,
)


class TemplateSourceType(str, Enum):
    COOKIECUTTER_REMOTE = "cookiecutter_remote"
    COPIER_REMOTE = "copier_remote"
    COOKIECUTTER_LOCAL = "cookiecutter_local"
    COPIER_LOCAL = "copier_local"
    COPIER_WITH_TASKS = "copier_with_tasks"
    COOKIECUTTER_CHANGES_TO_COPIER_REMOTE = "cookiecutter_changes_to_copier_remote"


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
    is_relative_template: bool = False
    version_migrate_func: Callable[[str], None] = lambda path: None
    self_migrate_func: Callable[
        ["TemplateSourceFixture"], None
    ] = lambda template_source: None
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

    @property
    def has_relative_path(self) -> bool:
        return self.is_local_template and not Path(self.path).is_absolute()

    @property
    def url_or_absolute_path(self) -> str:
        if not self.has_relative_path:
            return self.path
        # Must be local relative path. Paths are relative to config.GENERATED_REPO_DIR
        return str((config.GENERATED_REPO_DIR / Path(self.path)).resolve())

    def relative_path_relative_to(
        self, relative: Union[str, Path], orig_relative_to: Optional[Path] = None
    ) -> str:
        orig_relative_to = orig_relative_to or config.GENERATED_REPO_DIR
        if not self.has_relative_path:
            return self.path
        return os.path.relpath((orig_relative_to / self.path).resolve(), relative)

    def render_without_flexlate(self, path: Optional[Path] = None) -> CompletedProcess:
        path = path or config.GENERATED_REPO_DIR
        if self.template_type == TemplateType.COPIER:
            if self.is_local_template:
                use_path = self.path  # local templates already at v1 by default
            else:
                use_path = f"{self.path}.git --vcs-ref v1"
            return run(f"copier {use_path} {path}", input_data=self.input_data)
        elif self.template_type == TemplateType.COOKIECUTTER:
            if self.is_local_template:
                use_path = self.path  # local templates already at v1 by default
            else:
                use_path = f"{self.path} --checkout v1"
            # Need to wipe any local cache or it will ask whether to use it
            cache_path = Path("~").expanduser() / ".cookiecutters" / self.name
            if cache_path.exists():
                remove_folder(cache_path)
            with change_directory_to(path):
                return run(f"cookiecutter {use_path}", input_data=self.input_data)
        else:
            raise NotImplementedError(
                f"no handling for template type {self.template_type}"
            )

    def copy(self, **kwargs):
        new = deepcopy(self)
        for key, val in kwargs.items():
            setattr(new, key, val)
        return new

    def move(self, to: Path):
        if not self.is_local_template:
            return

        template_dir = to / self.name
        source_path = self.path
        shutil.copytree(source_path, template_dir)
        self.path = str(template_dir)

    def migrate_version(self, path: str):
        self.version_migrate_func(path)  # type: ignore
        self.self_migrate_func(self)  # type: ignore

    def setup_paths(
        self, relative_to: Optional[Path] = None
    ) -> "TemplateSourceFixture":
        """
        Sets up local paths for the template.

        This should be called first during the test run. It is called then
        rather than as part of the fixture setup because it needs to happen
        after the generated folder is set in conftest.py.
        :return:
        """
        out_template_source = self.copy()
        if not self.is_local_template:
            return out_template_source

        relative_to = relative_to or config.GENERATED_REPO_DIR

        if out_template_source.is_relative_template:
            out_template_source = os.path.relpath(out_template_source.path, relative_to)
        return out_template_source


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

cookiecutter_with_hooks_local_fixture: Final[
    TemplateSourceFixture
] = TemplateSourceFixture(
    name=COOKIECUTTER_WITH_HOOKS_NAME,
    path=str(COOKIECUTTER_WITH_HOOKS_DIR),
    type=TemplateSourceType.COOKIECUTTER_LOCAL,
    template_type=TemplateType.COOKIECUTTER,
    input_data=dict(a="z", c="f"),
    update_input_data=dict(a="n", c="q"),
    version_1=COOKIECUTTER_WITH_HOOKS_VERSION,
    version_2=COOKIECUTTER_WITH_HOOKS_MODIFIED_VERSION,
    is_local_template=True,
    version_migrate_func=modify_cookiecutter_one,
    render_relative_root_in_output=Path("{{ cookiecutter.a }}"),
    render_relative_root_in_template=Path("{{ cookiecutter.a }}"),
    evaluated_render_relative_root_in_output_creator=lambda data: Path(data["a"]),
    expect_local_applied_template_path=Path(".."),
)

copier_with_tasks_local_fixture: Final[TemplateSourceFixture] = TemplateSourceFixture(
    name=COPIER_WITH_TASKS_NAME,
    path=str(COPIER_WITH_TASKS_DIR),
    type=TemplateSourceType.COPIER_WITH_TASKS,
    template_type=TemplateType.COPIER,
    input_data=dict(q1="abc"),
    update_input_data=dict(q1="qwe"),
    version_1=COPIER_WITH_TASKS_VERSION,
    version_2=COPIER_WITH_TASKS_MODIFIED_VERSION,
    is_local_template=True,
    version_migrate_func=modify_copier_with_tasks,
)


def _update_cookiecutter_template_source_to_copier(
    template_source: TemplateSourceFixture,
):
    template_source.evaluated_render_relative_root_in_output_creator = (
        lambda data: Path(".")
    )
    template_source.render_relative_root_in_template = Path(".")
    template_source.render_relative_root_in_output = Path(".")
    template_source.expect_local_applied_template_path = Path(".")


COOKIECUTTER_CHANGES_TO_COPIER_LOCAL_FIXTURE: Final[
    TemplateSourceFixture
] = cookiecutter_local_fixture.copy(
    version_migrate_func=modify_cookiecutter_one_to_be_copier,
    version_2=COPIER_FROM_COOKIECUTTER_ONE_VERSION,
    self_migrate_func=_update_cookiecutter_template_source_to_copier,
)


COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_FIXTURE: Final[
    TemplateSourceFixture
] = TemplateSourceFixture(
    name=COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_NAME,
    path=COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_URL,
    type=TemplateSourceType.COOKIECUTTER_CHANGES_TO_COPIER_REMOTE,
    template_type=TemplateType.COOKIECUTTER,
    input_data=dict(a="z", c="f"),
    update_input_data=dict(a="n", c="q"),
    version_1=COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_VERSION_1,
    version_2=COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_VERSION_2,
    render_relative_root_in_output=Path("{{ cookiecutter.a }}"),
    render_relative_root_in_template=Path("{{ cookiecutter.a }}"),
    evaluated_render_relative_root_in_output_creator=lambda data: Path(data["a"]),
    expect_local_applied_template_path=Path(".."),
    self_migrate_func=_update_cookiecutter_template_source_to_copier,
)


local_absolute_path_fixtures: Final[List[TemplateSourceFixture]] = [
    cookiecutter_local_fixture,
    COPIER_LOCAL_FIXTURE,
    cookiecutter_with_hooks_local_fixture,
    copier_with_tasks_local_fixture,
]

remote_fixtures: Final[List[TemplateSourceFixture]] = [
    COOKIECUTTER_REMOTE_FIXTURE,
    COPIER_REMOTE_FIXTURE,
]

# Create relative path fixtures
local_relative_path_fixtures: Final[List[TemplateSourceFixture]] = [
    fixture.copy(is_relative_path=True) for fixture in local_absolute_path_fixtures
]


all_standard_template_source_fixtures: Final[List[TemplateSourceFixture]] = [
    *remote_fixtures,
    *local_absolute_path_fixtures,
]


@contextlib.contextmanager
def template_source_in_dir_if_local_template(
    orig_template_source: TemplateSourceFixture,
    dir: Path,
) -> ContextManager[TemplateSourceFixture]:
    out_template_source = orig_template_source.copy()
    if orig_template_source.is_local_template:
        # Copy into directory so it can be worked with without changing the original
        out_template_source.move(dir)
    yield out_template_source


@contextlib.contextmanager
def template_source_with_temp_dir_if_local_template(
    template_source: TemplateSourceFixture,
) -> ContextManager[TemplateSourceFixture]:
    with create_temp_path() as temp_path:
        with template_source_in_dir_if_local_template(
            template_source, temp_path
        ) as output_template_source:
            yield output_template_source


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
    with template_source_with_temp_dir_if_local_template(
        request.param
    ) as template_source:
        yield template_source


cookiecutter_changes_to_copier_fixtures = [
    COOKIECUTTER_CHANGES_TO_COPIER_LOCAL_FIXTURE,
    COOKIECUTTER_CHANGES_TO_COPIER_REMOTE_FIXTURE,
]


@pytest.fixture(scope="function", params=cookiecutter_changes_to_copier_fixtures)
def template_source_cookiecutter_changes_to_copier(request) -> TemplateSourceFixture:
    with template_source_with_temp_dir_if_local_template(
        request.param
    ) as template_source:
        yield template_source


COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH = COOKIECUTTER_REMOTE_FIXTURE.path
