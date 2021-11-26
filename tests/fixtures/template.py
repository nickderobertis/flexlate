import pytest

from flexlate.finder.cookiecutter import CookiecutterFinder
from flexlate.template.cookiecutter import CookiecutterTemplate
from tests.config import COOKIECUTTER_ONE_DIR


@pytest.fixture
def cookiecutter_one_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    yield finder.find(COOKIECUTTER_ONE_DIR)