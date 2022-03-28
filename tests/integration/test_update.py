from flexlate import Flexlate
from tests.integration.fixtures.template_source import (
    COOKIECUTTER_CHANGES_TO_COPIER_LOCAL_FIXTURE,
    template_source_with_temp_dir_if_local_template,
)
from tests.integration.fixtures.repo import *

fxt = Flexlate()


def test_update_template_from_cookiecutter_to_copier(
    repo_with_default_flexlate_project: Repo,
):
    with template_source_with_temp_dir_if_local_template(
        COOKIECUTTER_CHANGES_TO_COPIER_LOCAL_FIXTURE
    ) as template_source:
        with change_directory_to(GENERATED_REPO_DIR):
            fxt.add_template_source(template_source.path)
            fxt.apply_template_and_add(
                template_source.name, data=template_source.input_data, no_input=True
            )

            # Check that files are correct

            # Update local template, now it is a copier template
            template_source.version_migrate_func(template_source.url_or_absolute_path)

            # Should be anle to directly update even though template type changes
            fxt.update(data=[template_source.update_input_data], no_input=True)

            # Check that files are correct
