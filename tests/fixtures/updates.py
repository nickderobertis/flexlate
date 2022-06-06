import pytest

from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.update.template import TemplateUpdate
from tests import config
from tests.fixtures.template import cookiecutter_one_template


@pytest.fixture
def cookiecutter_one_update_no_data(
    cookiecutter_one_template: CookiecutterTemplate,
) -> TemplateUpdate:
    return TemplateUpdate(
        template=cookiecutter_one_template,
        config_location=config.GENERATED_FILES_DIR / "flexlate.json",
        index=0,
    )
