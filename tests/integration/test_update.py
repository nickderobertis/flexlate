from pathlib import Path

from flexlate import Flexlate
from flexlate.template.types import TemplateType
from tests import config as test_config
from tests.integration.fixtures.repo import *
from tests.integration.fixtures.template_source import (
    COOKIECUTTER_CHANGES_TO_COPIER_LOCAL_FIXTURE,
    COPIER_LOCAL_FIXTURE,
    TemplateSourceFixture,
    template_source_cookiecutter_changes_to_copier,
    template_source_with_temp_dir_if_local_template,
)
from tests.integration.template_source_checks import (
    assert_root_template_source_output_is_correct,
)

fxt = Flexlate()


def test_update_template_from_cookiecutter_to_copier(
    repo_with_default_flexlate_project: Repo,
    template_source_cookiecutter_changes_to_copier: TemplateSourceFixture,
):
    template_source = template_source_cookiecutter_changes_to_copier

    def assert_template_type_is(template_type: TemplateType):
        config = FlexlateConfig.load(test_config.GENERATED_REPO_DIR / "flexlate.json")
        assert len(config.template_sources) == 1
        ts = config.template_sources[0]
        assert ts.type == template_type

    with change_directory_to(test_config.GENERATED_REPO_DIR):
        fxt.add_template_source(
            template_source.path, target_version=template_source.version_1
        )
        fxt.apply_template_and_add(
            template_source.name, data=template_source.input_data, no_input=True
        )

        # Check that files are correct
        assert_root_template_source_output_is_correct(
            template_source,
            after_version_update=False,
            after_data_update=False,
            target_version=template_source.version_1,
        )
        assert_template_type_is(TemplateType.COOKIECUTTER)

        # Update local template, now it is a copier template
        template_source.migrate_version(template_source.url_or_absolute_path)

        # Remove targeting to version 1
        fxt.update_template_source_target_version(template_source.name)

        # Should be anle to directly update even though template type changes
        fxt.update(data=[template_source.update_input_data], no_input=True)

        # Check that files are correct
        assert_root_template_source_output_is_correct(
            template_source,
            after_version_update=True,
            after_data_update=True,
        )
        assert_template_type_is(TemplateType.COPIER)


def test_update_template_with_relative_path_from_outside_project(
    repo_with_default_flexlate_project: Repo,
):
    update_from_dir = test_config.GENERATED_FILES_DIR / "something"
    update_from_dir.mkdir()

    project_dir = test_config.GENERATED_REPO_DIR

    with template_source_with_temp_dir_if_local_template(
        COPIER_LOCAL_FIXTURE
    ) as template_source:
        # First set up project so it can be updated
        with change_directory_to(project_dir):
            fxt.add_template_source(template_source.path)
            fxt.apply_template_and_add(
                template_source.name, data=template_source.input_data, no_input=True
            )

            # Check that files are correct
            assert_root_template_source_output_is_correct(
                template_source,
                after_version_update=False,
                after_data_update=False,
            )

            # Update local template
            template_source.migrate_version(template_source.url_or_absolute_path)

        # Now update from outside project
        with change_directory_to(update_from_dir):
            # Should be anle to directly update even though template type changes
            fxt.update(
                data=[template_source.update_input_data],
                no_input=True,
                project_path=Path("..") / "project",
            )

        # Check that files are correct
        assert_root_template_source_output_is_correct(
            template_source,
            after_version_update=True,
            after_data_update=True,
        )
