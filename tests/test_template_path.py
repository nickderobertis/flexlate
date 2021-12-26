import pytest

from flexlate.template_path import is_repo_url
from tests.config import COOKIECUTTER_ONE_DIR, COOKIECUTTER_REMOTE_URL


@pytest.mark.parametrize(
    "path, path_is_repo_url",
    [
        (str(COOKIECUTTER_ONE_DIR), False),
        ("Aasdfssdfkj", False),
        # https format
        (COOKIECUTTER_REMOTE_URL, True),
        (COOKIECUTTER_REMOTE_URL + ".git", True),
        ("git@github.com:nickderobertis/copier-simple-example.git", True),
        ("git@github.com:nickderobertis/copier-simple-example", True),
    ],
)
def test_is_repo_url(path: str, path_is_repo_url: bool):
    assert is_repo_url(path) == path_is_repo_url
