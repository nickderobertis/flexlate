from typing import List

import pytest

from flexlate.render.multi import MultiRenderer
from flexlate.render.specific.cookiecutter import CookiecutterRenderer
from flexlate.template.cookiecutter import CookiecutterTemplate
from tests.config import GENERATED_FILES_DIR
from tests.dirutils import wipe_generated_folder
from tests.fixtures.template import *

COOKIECUTTER_ONE_GENERATED_TEXT_PATH = GENERATED_FILES_DIR / "b" / "text.txt"
COOKIECUTTER_TWO_GENERATED_TEXT_PATH = GENERATED_FILES_DIR / "b" / "text2.txt"


def _cookiecutter_one_generated_text_content() -> str:
    assert COOKIECUTTER_ONE_GENERATED_TEXT_PATH.exists()
    return COOKIECUTTER_ONE_GENERATED_TEXT_PATH.read_text()


def _cookiecutter_two_generated_text_content() -> str:
    assert COOKIECUTTER_TWO_GENERATED_TEXT_PATH.exists()
    return COOKIECUTTER_TWO_GENERATED_TEXT_PATH.read_text()


@pytest.fixture(autouse=True)
def before_each():
    wipe_generated_folder()


def test_render_cookiecutter_with_defaults(
    cookiecutter_one_template: CookiecutterTemplate,
):
    renderer = CookiecutterRenderer()
    renderer.render(cookiecutter_one_template, out_path=GENERATED_FILES_DIR)
    assert _cookiecutter_one_generated_text_content() == ""


def test_render_cookiecutter_with_data(
    cookiecutter_one_template: CookiecutterTemplate,
):
    renderer = CookiecutterRenderer()
    renderer.render(
        cookiecutter_one_template, out_path=GENERATED_FILES_DIR, data={"c": "something"}
    )
    assert _cookiecutter_one_generated_text_content() == "something"


def test_render_multi_with_defaults(cookiecutter_templates: List[CookiecutterTemplate]):
    renderer = MultiRenderer()
    renderer.render(
        cookiecutter_templates, out_path=GENERATED_FILES_DIR
    )
    assert _cookiecutter_one_generated_text_content() == ""
    assert _cookiecutter_two_generated_text_content() == "e"
