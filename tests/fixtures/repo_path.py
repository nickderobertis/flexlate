from dataclasses import dataclass
from typing import Final, List

import pytest

from tests.config import COOKIECUTTER_ONE_DIR, COOKIECUTTER_REMOTE_URL


@dataclass
class RepoPathFixture:
    path: str
    is_repo_url: bool
    is_local_path: bool


repo_path_fixtures: Final[List[RepoPathFixture]] = [
    RepoPathFixture(str(COOKIECUTTER_ONE_DIR), False, True),
    RepoPathFixture("Aasdfssdfkj", False, False),
    RepoPathFixture(COOKIECUTTER_REMOTE_URL, True, False),
    RepoPathFixture(COOKIECUTTER_REMOTE_URL + ".git", True, False),
    RepoPathFixture(
        "git@github.com:nickderobertis/copier-simple-example.git", True, False
    ),
    RepoPathFixture("git@github.com:nickderobertis/copier-simple-example", True, False),
]


@pytest.fixture(scope="module", params=repo_path_fixtures)
def repo_path_fixture(request) -> RepoPathFixture:
    yield request.param
