import pytest

from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.update.template import TemplateUpdate
from tests.config import GENERATED_FILES_DIR
from tests.fixtures.template import cookiecutter_one_template


@pytest.fixture
def cookiecutter_one_update_no_data(
    cookiecutter_one_template: CookiecutterTemplate,
) -> TemplateUpdate:
    return TemplateUpdate(
        template=cookiecutter_one_template,
        config_location=GENERATED_FILES_DIR / "flexlate.json",
        index=0,
    )
