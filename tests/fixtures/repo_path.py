from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, List, Callable, Optional

import pytest

from tests.config import (
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_ONE_NAME,
    COOKIECUTTER_REMOTE_NAME,
    COPIER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_VERSION_2,
    COPIER_REMOTE_VERSION_2,
    COOKIECUTTER_REMOTE_VERSION_1,
    COPIER_REMOTE_VERSION_1,
)
from tests.fixtures.template import (
    get_header_for_cookiecutter_remote_template,
    get_footer_for_copier_remote_template,
)


@dataclass
class RepoPathFixture:
    path: str
    name: str
    is_repo_url: bool
    is_local_path: bool
    is_ssh_url: bool = False
    default_version: Optional[str] = None
    versions: List[Optional[str]] = field(default_factory=lambda: [None])
    assert_was_cloned_correctly: Optional[Callable[[Path, Optional[str]], None]] = None


def assert_cookiecutter_remote_was_cloned_correctly(path: Path, version: Optional[str]):
    expect_file = path / "{{ cookiecutter.name }}" / "{{ cookiecutter.name }}.txt"
    header = get_header_for_cookiecutter_remote_template(
        version or COOKIECUTTER_REMOTE_VERSION_2
    )
    assert expect_file.read_text() == header + "{{ cookiecutter.key }}"


def assert_copier_remote_was_cloned_correctly(path: Path, version: Optional[str]):
    expect_file = path / "output" / "{{ question1 }}.txt.jinja"
    footer = get_footer_for_copier_remote_template(version or COPIER_REMOTE_VERSION_2)
    assert expect_file.read_text() == "{{ question2 }}" + footer


repo_path_fixtures: Final[List[RepoPathFixture]] = [
    RepoPathFixture(str(COOKIECUTTER_ONE_DIR), COOKIECUTTER_ONE_NAME, False, True),
    RepoPathFixture("Aasdfssdfkj", "Aasdfssdfkj", False, False),
    RepoPathFixture(
        COOKIECUTTER_REMOTE_URL,
        COOKIECUTTER_REMOTE_NAME,
        True,
        False,
        default_version=COOKIECUTTER_REMOTE_VERSION_2,
        versions=[COOKIECUTTER_REMOTE_VERSION_1, None],
        assert_was_cloned_correctly=assert_cookiecutter_remote_was_cloned_correctly,
    ),
    RepoPathFixture(
        COOKIECUTTER_REMOTE_URL + ".git",
        COOKIECUTTER_REMOTE_NAME,
        True,
        False,
        default_version=COOKIECUTTER_REMOTE_VERSION_2,
        versions=[COOKIECUTTER_REMOTE_VERSION_1, None],
        assert_was_cloned_correctly=assert_cookiecutter_remote_was_cloned_correctly,
    ),
    RepoPathFixture(
        "git@github.com:nickderobertis/copier-simple-example.git",
        COPIER_REMOTE_NAME,
        True,
        False,
        is_ssh_url=True,
        default_version=COPIER_REMOTE_VERSION_2,
        versions=[COPIER_REMOTE_VERSION_1, None],
        assert_was_cloned_correctly=assert_copier_remote_was_cloned_correctly,
    ),
    RepoPathFixture(
        "git@github.com:nickderobertis/copier-simple-example",
        COPIER_REMOTE_NAME,
        True,
        False,
        is_ssh_url=True,
        default_version=COPIER_REMOTE_VERSION_2,
        versions=[COPIER_REMOTE_VERSION_1, None],
        assert_was_cloned_correctly=assert_copier_remote_was_cloned_correctly,
    ),
]

repo_path_non_ssh_fixtures: Final[List[RepoPathFixture]] = [
    fixture for fixture in repo_path_fixtures if fixture.is_ssh_url == False
]


@pytest.fixture(scope="module", params=repo_path_fixtures)
def repo_path_fixture(request) -> RepoPathFixture:
    yield request.param


@pytest.fixture(scope="module", params=repo_path_non_ssh_fixtures)
def repo_path_non_ssh_fixture(request) -> RepoPathFixture:
    yield request.param
