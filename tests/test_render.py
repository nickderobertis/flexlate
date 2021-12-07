from flexlate.render.multi import MultiRenderer
from flexlate.render.renderable import Renderable
from flexlate.render.specific.cookiecutter import CookiecutterRenderer
from tests.config import GENERATED_FILES_DIR
from tests.dirutils import wipe_generated_folder
from tests.fileutils import (
    cookiecutter_one_generated_text_content,
    cookiecutter_two_generated_text_content,
)
from tests.fixtures.template import *
from tests.fixtures.renderable import *


@pytest.fixture(autouse=True)
def before_each():
    wipe_generated_folder()


def test_render_cookiecutter_with_defaults(
    cookiecutter_one_renderable: Renderable,
):
    renderer = CookiecutterRenderer()
    data = renderer.render(cookiecutter_one_renderable, no_input=True)
    assert data == {"a": "b", "c": ""}
    assert cookiecutter_one_generated_text_content() == ""


def test_render_cookiecutter_with_data(
    cookiecutter_one_renderable: Renderable,
):
    renderer = CookiecutterRenderer()
    cookiecutter_one_renderable.data = {"c": "something"}
    data = renderer.render(
        cookiecutter_one_renderable,
        no_input=True,
    )
    assert data == {"a": "b", "c": "something"}
    assert cookiecutter_one_generated_text_content() == "something"


def test_render_multi_with_defaults(cookiecutter_local_renderables: List[Renderable]):
    renderer = MultiRenderer()
    data = renderer.render(
        cookiecutter_local_renderables, project_root=GENERATED_FILES_DIR, no_input=True
    )
    assert data == [{"a": "b", "c": ""}, {"a": "b", "d": "e"}]
    assert cookiecutter_one_generated_text_content() == ""
    assert cookiecutter_two_generated_text_content() == "e"


def test_render_multi_with_data(cookiecutter_local_renderables: List[Renderable]):
    renderer = MultiRenderer()
    cookiecutter_local_renderables[0].data = {"a": "z", "c": "something"}
    cookiecutter_local_renderables[1].data = {"a": "z", "d": "f"}
    data = renderer.render(
        cookiecutter_local_renderables,
        project_root=GENERATED_FILES_DIR,
        no_input=True,
    )
    assert data == [{"a": "z", "c": "something"}, {"a": "z", "d": "f"}]
    assert cookiecutter_one_generated_text_content(folder="z") == "something"
    assert cookiecutter_two_generated_text_content(folder="z") == "f"


def test_render_multi_with_overlap(
    cookiecutter_one_renderable: Renderable,
):
    renderer = MultiRenderer()

    data = renderer.render(
        [
            cookiecutter_one_renderable.copy(update=dict(data={"c": "something"})),
            cookiecutter_one_renderable.copy(update=dict(data={"c": "something else"})),
        ],
        no_input=True,
    )
    assert data == [{"a": "b", "c": "something"}, {"a": "b", "c": "something else"}]
    assert cookiecutter_one_generated_text_content() == "somethingsomething else"
