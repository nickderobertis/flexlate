from flexlate.render.renderable import Renderable
from flexlate.template.copier import CopierTemplate
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.template import *


@pytest.fixture
def cookiecutter_one_renderable(
    cookiecutter_one_template: CookiecutterTemplate,
) -> Renderable:
    return Renderable(template=cookiecutter_one_template, out_root=GENERATED_FILES_DIR)


@pytest.fixture
def copier_one_renderable(
    copier_one_template: CopierTemplate,
) -> Renderable:
    return Renderable(template=copier_one_template, out_root=GENERATED_FILES_DIR)


@pytest.fixture
def copier_output_subdir_renderable(
    copier_output_subdir_template: CopierTemplate,
) -> Renderable:
    return Renderable(
        template=copier_output_subdir_template, out_root=GENERATED_FILES_DIR
    )


@pytest.fixture
def cookiecutter_two_renderable(
    cookiecutter_two_template: CookiecutterTemplate,
) -> Renderable:
    return Renderable(template=cookiecutter_two_template, out_root=GENERATED_FILES_DIR)


@pytest.fixture
def cookiecutter_local_renderables(
    cookiecutter_one_renderable: Renderable, cookiecutter_two_renderable: Renderable
) -> List[Renderable]:
    return [cookiecutter_one_renderable, cookiecutter_two_renderable]
