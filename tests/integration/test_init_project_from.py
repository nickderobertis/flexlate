from pathlib import Path

from flexlate import Flexlate
from flexlate.path_ops import change_directory_to
from tests.config import GENERATED_FILES_DIR
from tests.integration.fixtures.template_source import (
    template_source_with_temp_dir_if_local_template,
    COPIER_LOCAL_FIXTURE,
    TemplateSourceFixture,
    template_source_in_dir_if_local_template,
)
from tests.integration.template_source_checks import (
    assert_root_template_source_output_is_correct,
    assert_template_source_output_is_correct,
)

fxt = Flexlate()


def _init_project_from_template_dir_into_parent(template_source: TemplateSourceFixture):
    template_path = Path(template_source.path)
    with change_directory_to(template_path):
        folder = fxt.init_project_from(
            ".", path=Path(".."), no_input=True, data=template_source.input_data
        )

    project_path = template_path.parent / folder
    assert_template_source_output_is_correct(
        template_source, project_path, override_template_source_path="../one"
    )


def test_init_project_from_template_dir_in_temp_dir_into_parent():
    with template_source_with_temp_dir_if_local_template(
        COPIER_LOCAL_FIXTURE
    ) as template_source:
        _init_project_from_template_dir_into_parent(template_source)


def test_init_project_from_template_dir_in_user_dir_into_parent():
    with template_source_in_dir_if_local_template(
        COPIER_LOCAL_FIXTURE,
        GENERATED_FILES_DIR,
    ) as template_source:
        _init_project_from_template_dir_into_parent(template_source)
