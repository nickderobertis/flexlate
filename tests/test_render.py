import pytest

from flexlate.render.cookiecutter import CookiecutterRenderer
from flexlate.template.cookiecutter import CookiecutterTemplate
from tests.config import GENERATED_FILES_DIR
from tests.dirutils import wipe_generated_folder
from tests.fixtures.template import cookiecutter_one_template

COOKIECUTTER_ONE_GENERATED_TEXT_PATH = GENERATED_FILES_DIR / "b" / "text.txt"


def _cookiecutter_one_generated_text_content() -> str:
    assert COOKIECUTTER_ONE_GENERATED_TEXT_PATH.exists()
    return COOKIECUTTER_ONE_GENERATED_TEXT_PATH.read_text()


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
