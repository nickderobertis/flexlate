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
    assert template.version == "d512c7e14e83cb4bc8d4e5ae06bb357e"
    assert template.config.defaults == {"a": "b", "c": ""}


def test_get_cookiecutter_remote_template():
    finder = CookiecutterFinder()
    template = finder.find(COOKIECUTTER_REMOTE_URL)
    assert (
        template.path
        == Path("~").expanduser() / ".cookiecutters" / "cookiecutter-simple-example"
    )
    assert template.version == "c390901c4fd599473bdb95fa4dd3d2a6eb2b34f0"
    assert template.config.defaults == {"name": "abc", "key": "value"}
