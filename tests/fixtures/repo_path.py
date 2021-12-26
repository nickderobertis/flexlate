from dataclasses import dataclass
from pathlib import Path
from typing import Final, List, Callable, Optional

import pytest

from tests.config import (
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_ONE_NAME,
    COOKIECUTTER_REMOTE_NAME,
    COPIER_REMOTE_NAME,
)


@dataclass
class RepoPathFixture:
    path: str
    name: str
    is_repo_url: bool
    is_local_path: bool
    is_ssh_url: bool = False
    was_cloned_correctly: Optional[Callable[[Path], bool]] = None


def cookiecutter_remote_was_cloned_correctly(path: Path) -> bool:
    expect_file = path / "{{ cookiecutter.name }}" / "{{ cookiecutter.name }}.txt"
    return expect_file.read_text() == "some new header\n{{ cookiecutter.key }}"


def copier_remote_was_cloned_correctly(path: Path) -> bool:
    expect_file = path / "output" / "{{ question1 }}.txt.jinja"
    return expect_file.read_text() == "{{ question2 }}\nsome new footer"


repo_path_fixtures: Final[List[RepoPathFixture]] = [
    RepoPathFixture(str(COOKIECUTTER_ONE_DIR), COOKIECUTTER_ONE_NAME, False, True),
    RepoPathFixture("Aasdfssdfkj", "Aasdfssdfkj", False, False),
    RepoPathFixture(
        COOKIECUTTER_REMOTE_URL,
        COOKIECUTTER_REMOTE_NAME,
        True,
        False,
        was_cloned_correctly=cookiecutter_remote_was_cloned_correctly,
    ),
    RepoPathFixture(
        COOKIECUTTER_REMOTE_URL + ".git",
        COOKIECUTTER_REMOTE_NAME,
        True,
        False,
        was_cloned_correctly=cookiecutter_remote_was_cloned_correctly,
    ),
    RepoPathFixture(
        "git@github.com:nickderobertis/copier-simple-example.git",
        COPIER_REMOTE_NAME,
        True,
        False,
        is_ssh_url=True,
        was_cloned_correctly=copier_remote_was_cloned_correctly,
    ),
    RepoPathFixture(
        "git@github.com:nickderobertis/copier-simple-example",
        COPIER_REMOTE_NAME,
        True,
        False,
        is_ssh_url=True,
        was_cloned_correctly=copier_remote_was_cloned_correctly,
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
