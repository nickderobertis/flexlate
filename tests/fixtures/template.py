from typing import List

import pytest

from flexlate.finder.cookiecutter import CookiecutterFinder
from flexlate.template.cookiecutter import CookiecutterTemplate
from tests.config import COOKIECUTTER_ONE_DIR, COOKIECUTTER_TWO_DIR


@pytest.fixture
def cookiecutter_one_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    yield finder.find(COOKIECUTTER_ONE_DIR)


@pytest.fixture
def cookiecutter_two_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    yield finder.find(COOKIECUTTER_TWO_DIR)


@pytest.fixture
def cookiecutter_templates(
    cookiecutter_one_template: CookiecutterTemplate,
    cookiecutter_two_template: CookiecutterTemplate,
) -> List[CookiecutterTemplate]:
    yield [cookiecutter_one_template, cookiecutter_two_template]
