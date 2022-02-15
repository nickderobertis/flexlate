from flexlate.render.multi import MultiRenderer
from flexlate.render.renderable import Renderable
from flexlate.render.specific.cookiecutter import CookiecutterRenderer
from flexlate.render.specific.copier import CopierRenderer
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
    assert cookiecutter_one_generated_text_content() == "b"


def test_render_copier_with_defaults(copier_one_renderable: Renderable):
    renderer = CopierRenderer()
    data = renderer.render(copier_one_renderable, no_input=True)
    assert data == {"q1": "a1", "q2": 1, "q3": None}
    rendered_path = GENERATED_FILES_DIR / "a1.txt"
    assert rendered_path.read_text() == "1"


def test_render_copier_subdir_with_defaults(
    copier_output_subdir_renderable: Renderable,
):
    renderer = CopierRenderer()
    renderable = copier_output_subdir_renderable
    data = renderer.render(renderable, no_input=True)
    assert data == {"qone": "aone", "qtwo": "atwo"}
    rendered_path = GENERATED_FILES_DIR / "aone.txt"
    assert rendered_path.read_text() == "atwo"
    should_not_exist_path = GENERATED_FILES_DIR / "not-rendered.txt"
    assert not should_not_exist_path.exists()


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
    assert cookiecutter_one_generated_text_content() == "bsomething"


def test_render_copier_with_data(copier_one_renderable: Renderable):
    renderer = CopierRenderer()
    copier_one_renderable.data = {"q2": 2, "q3": "a3"}
    data = renderer.render(copier_one_renderable, no_input=True)
    assert data == {"q1": "a1", "q2": 2, "q3": "a3"}
    rendered_path = GENERATED_FILES_DIR / "a1.txt"
    assert rendered_path.read_text() == "2"


def test_render_multi_with_defaults(cookiecutter_local_renderables: List[Renderable]):
    renderer = MultiRenderer()
    data = renderer.render(
        cookiecutter_local_renderables, project_root=GENERATED_FILES_DIR, no_input=True
    )
    assert data == [{"a": "b", "c": ""}, {"a": "b", "d": "e"}]
    assert cookiecutter_one_generated_text_content() == "b"
    assert cookiecutter_two_generated_text_content() == "e"


def test_render_multi_with_copier_defaults(copier_one_renderable: Renderable):
    renderer = MultiRenderer()
    data = renderer.render(
        [copier_one_renderable], project_root=GENERATED_FILES_DIR, no_input=True
    )
    assert data == [{"q1": "a1", "q2": 1, "q3": None}]
    rendered_path = GENERATED_FILES_DIR / "a1.txt"
    assert rendered_path.read_text() == "1"


def test_render_multi_with_data(
    cookiecutter_local_renderables: List[Renderable], copier_one_renderable: Renderable
):
    renderer = MultiRenderer()
    cookiecutter_local_renderables[0].data = {"a": "z", "c": "something"}
    cookiecutter_local_renderables[1].data = {"a": "z", "d": "f"}
    copier_one_renderable.data = {"q2": 2, "q3": "a3"}
    data = renderer.render(
        [*cookiecutter_local_renderables, copier_one_renderable],
        project_root=GENERATED_FILES_DIR,
        no_input=True,
    )
    assert data == [
        {"a": "z", "c": "something"},
        {"a": "z", "d": "f"},
        {"q1": "a1", "q2": 2, "q3": "a3"},
    ]
    assert cookiecutter_one_generated_text_content(folder="z") == "zsomething"
    assert cookiecutter_two_generated_text_content(folder="z") == "f"
    copier_rendered_path = GENERATED_FILES_DIR / "a1.txt"
    assert copier_rendered_path.read_text() == "2"


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
    assert cookiecutter_one_generated_text_content() == "bsomethingbsomething else"


def test_render_string_local_cookiecutter(
    cookiecutter_one_renderable: Renderable,
):
    renderer = CookiecutterRenderer()
    output = renderer.render_string(
        "{{ cookiecutter.a }} works", cookiecutter_one_renderable
    )
    assert output == "b works"
