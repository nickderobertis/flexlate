from pathlib import Path

from flexlate.finder.cookiecutter import CookiecutterFinder
from tests.config import COOKIECUTTER_ONE_DIR, COOKIECUTTER_REMOTE_URL


def test_get_cookiecutter_config():
    finder = CookiecutterFinder()
    config = finder.get_config(COOKIECUTTER_ONE_DIR)
    assert config.defaults == {"a": "b", "c": ""}


def test_get_cookiecutter_local_template():
    finder = CookiecutterFinder()
    template = finder.find(COOKIECUTTER_ONE_DIR)
    assert template.path == COOKIECUTTER_ONE_DIR
    assert template.config.defaults == {"a": "b", "c": ""}


def test_get_cookiecutter_remote_template():
    finder = CookiecutterFinder()
    template = finder.find(COOKIECUTTER_REMOTE_URL)
    assert (
        template.path
        == Path("~").expanduser() / ".cookiecutters" / "cookiecutter-simple-example"
    )
    assert template.config.defaults == {"name": "abc", "key": "value"}
