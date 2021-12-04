from pathlib import Path

import pytest

from flexlate.finder.multi import MultiFinder
from flexlate.finder.specific.cookiecutter import CookiecutterFinder
from tests.config import (
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_VERSION_1,
    COOKIECUTTER_REMOTE_VERSION_2, COOKIECUTTER_ONE_VERSION,
)


def test_get_cookiecutter_config():
    finder = CookiecutterFinder()
    config = finder.get_config(COOKIECUTTER_ONE_DIR)
    assert config.defaults == {"a": "b", "c": ""}


def test_get_cookiecutter_local_template():
    finder = CookiecutterFinder()
    template = finder.find(COOKIECUTTER_ONE_DIR)
    assert template.path == COOKIECUTTER_ONE_DIR
    assert template.git_url is None
    assert template.version == COOKIECUTTER_ONE_VERSION
    assert template.config.defaults == {"a": "b", "c": ""}


@pytest.mark.parametrize(
    "version, expect_contents",
    [
        (COOKIECUTTER_REMOTE_VERSION_1, "{{ cookiecutter.key }}"),
        (COOKIECUTTER_REMOTE_VERSION_2, "some new header\n{{ cookiecutter.key }}"),
    ],
)
def test_get_cookiecutter_remote_template(version: str, expect_contents: str):
    finder = CookiecutterFinder()
    template = finder.find(COOKIECUTTER_REMOTE_URL, version=version)
    assert (
        template.path
        == Path("~").expanduser() / ".cookiecutters" / "cookiecutter-simple-example"
    )
    assert template.git_url == COOKIECUTTER_REMOTE_URL
    assert template.version == version
    assert template.config.defaults == {"name": "abc", "key": "value"}
    template_file = (
        template.path / "{{ cookiecutter.name }}" / "{{ cookiecutter.name }}.txt"
    )
    assert template_file.read_text() == expect_contents


def test_multi_finder_get_cookiecutter_local_template():
    finder = MultiFinder()
    template = finder.find(COOKIECUTTER_ONE_DIR)
    assert template.path == COOKIECUTTER_ONE_DIR
    assert template.git_url is None
    assert template.version == COOKIECUTTER_ONE_VERSION
    assert template.config.defaults == {"a": "b", "c": ""}


@pytest.mark.parametrize(
    "version, expect_contents",
    [
        (COOKIECUTTER_REMOTE_VERSION_1, "{{ cookiecutter.key }}"),
        (COOKIECUTTER_REMOTE_VERSION_2, "some new header\n{{ cookiecutter.key }}"),
    ],
)
def test_multi_finder_get_cookiecutter_remote_template(
    version: str, expect_contents: str
):
    finder = MultiFinder()
    template = finder.find(COOKIECUTTER_REMOTE_URL, version=version)
    assert (
        template.path
        == Path("~").expanduser() / ".cookiecutters" / "cookiecutter-simple-example"
    )
    assert template.git_url == COOKIECUTTER_REMOTE_URL
    assert template.version == version
    assert template.config.defaults == {"name": "abc", "key": "value"}
    template_file = (
        template.path / "{{ cookiecutter.name }}" / "{{ cookiecutter.name }}.txt"
    )
    assert template_file.read_text() == expect_contents
