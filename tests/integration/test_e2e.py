# Integration tests
import contextlib
import os
import shutil
from pathlib import Path
from typing import Optional, Callable, cast
from unittest.mock import patch

import appdirs
import pytest
from _pytest.capture import CaptureFixture
from click.testing import Result
from git import GitCommandError

from flexlate.add_mode import AddMode
from flexlate.branch_update import (
    get_flexlate_branch_name,
    get_flexlate_branch_name_for_feature_branch,
)
from flexlate.config import FlexlateConfig, FlexlateProjectConfig
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.exc import TriedToCommitButNoChangesException, UnnecessarySyncException
from flexlate.ext_git import merge_branch_into_current
from flexlate.main import Flexlate
from flexlate.template.types import TemplateType
from flexlate.template_data import TemplateData
from tests.config import (
    GENERATED_FILES_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_VERSION_2,
)
from tests.fixtures.git import *
from tests.fixtures.subdir_style import SubdirStyle, subdir_style, subdir_style_or_none
from tests.fixtures.template import (
    CookiecutterRemoteTemplateData,
    get_header_for_cookiecutter_remote_template,
    get_footer_for_copier_remote_template,
    get_footer_for_cookiecutter_local_template,
    get_footer_for_copier_local_template,
)
from tests.fixtures.cli import (
    FlexlateFixture,
    FlexlateType,
    flexlates,
    flexlates_ignore_cli_exceptions,
)
from tests.fixtures.add_mode import add_mode
from tests.integration.fixtures.template_source import (
    TemplateSourceFixture,
    template_source,
    template_source_one_remote_and_all_local_relative,
    template_source_with_relative,
    TemplateSourceType,
    COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH,
    COPIER_LOCAL_FIXTURE,
    COOKIECUTTER_REMOTE_FIXTURE,
    template_source_with_temp_dir_if_local_template,
    COPIER_REMOTE_FIXTURE,
)
from tests.gitutils import (
    assert_main_commit_message_matches,
    checkout_new_branch,
    checkout_existing_branch,
)
from tests.integration.cli_stub import CLIRunnerException, capture_output
from tests.integration.undoables import UNDOABLE_OPERATIONS
from tests.test_pusher import add_local_remote_and_check_branches_on_exit


def test_init_project_and_add_source_and_template(
    flexlates: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
    template_source: TemplateSourceFixture,
):
    fxt = flexlates.flexlate
    no_input = flexlates.type == FlexlateType.APP
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(template_source.path)
        fxt.apply_template_and_add(
            template_source.name, data=template_source.input_data, no_input=no_input
        )

    _assert_project_files_are_correct(
        expect_data=template_source.input_data,
        template_source_type=template_source.type,
        version=template_source.default_version,
    )
    config_relative_root = (
        template_source.evaluated_render_relative_root_in_output_creator(
            template_source.input_data
        )
    )
    _assert_config_is_correct(
        at_config_path=GENERATED_REPO_DIR / config_relative_root / "flexlate.json",
        expect_applied_template_root=template_source.expect_local_applied_template_path,
        expect_data=template_source.input_data,
        template_source_type=template_source.type,
        version=template_source.default_version,
        name=template_source.name,
        url=template_source.url,
        path=template_source.path,
        render_relative_root_in_output=template_source.render_relative_root_in_output,
        render_relative_root_in_template=template_source.render_relative_root_in_template,
    )

    project_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=False)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_init_project_for_user_and_add_source_and_template(
    flexlates: FlexlateFixture,
    add_mode: AddMode,
    repo_with_placeholder_committed: Repo,
):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(user=True, default_add_mode=add_mode)
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)

    _assert_project_files_are_correct()

    if add_mode == AddMode.USER:
        at_config_root = GENERATED_FILES_DIR
        ts_config_root = GENERATED_FILES_DIR
        template_root = GENERATED_REPO_DIR.absolute()
    elif add_mode == AddMode.PROJECT:
        at_config_root = GENERATED_REPO_DIR
        ts_config_root = GENERATED_REPO_DIR
        template_root = Path(".")
    elif add_mode == AddMode.LOCAL:
        at_config_root = GENERATED_REPO_DIR / "abc"
        ts_config_root = GENERATED_REPO_DIR
        template_root = Path("..")
    else:
        raise ValueError(f"unsupported add mode {add_mode}")

    _assert_config_is_correct(
        at_config_path=at_config_root / "flexlate.json",
        ts_config_path=ts_config_root / "flexlate.json",
        expect_applied_template_root=template_root,
        expect_add_mode=add_mode,
    )

    project_config_path = GENERATED_FILES_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=True, add_mode=add_mode)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_init_project_and_add_source_and_template_in_subdir(
    flexlates: FlexlateFixture,
    add_mode: AddMode,
    subdir_style: SubdirStyle,
    repo_with_placeholder_committed: Repo,
    template_source_one_remote_and_all_local_relative: TemplateSourceFixture,
):
    fxt = flexlates.flexlate
    template_source = template_source_one_remote_and_all_local_relative
    repo = repo_with_placeholder_committed

    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(default_add_mode=add_mode)
        fxt.add_template_source(template_source.path)
        subdir = GENERATED_REPO_DIR / "subdir1" / "subdir2"
        subdir.mkdir(parents=True)
        if subdir_style == SubdirStyle.CD:
            with change_directory_to(subdir):
                fxt.apply_template_and_add(template_source.name, no_input=True)
        elif subdir_style == SubdirStyle.PROVIDE_RELATIVE:
            fxt.apply_template_and_add(
                template_source.name,
                no_input=True,
                out_root=subdir.relative_to(os.getcwd()),
            )
        elif subdir_style == SubdirStyle.PROVIDE_ABSOLUTE:
            fxt.apply_template_and_add(
                template_source.name, no_input=True, out_root=subdir.absolute()
            )

    _assert_project_files_are_correct(
        subdir,
        template_source_type=template_source.type,
        version=template_source.default_version,
    )

    config_relative_root = (
        template_source.evaluated_render_relative_root_in_output_creator(
            _get_default_data(template_source.type)
        )
    )

    if add_mode == AddMode.LOCAL:
        applied_config_dir = subdir / config_relative_root
        expect_applied_template_root = (
            template_source.expect_local_applied_template_path
        )
        template_sources_config_dir = GENERATED_REPO_DIR
        expect_template_source_path = template_source.path
    elif add_mode == AddMode.PROJECT:
        applied_config_dir = GENERATED_REPO_DIR
        expect_applied_template_root = subdir.relative_to(GENERATED_REPO_DIR)
        template_sources_config_dir = GENERATED_REPO_DIR
        expect_template_source_path = template_source.path
    elif add_mode == AddMode.USER:
        applied_config_dir = GENERATED_FILES_DIR
        expect_applied_template_root = subdir.absolute()
        template_sources_config_dir = GENERATED_FILES_DIR
        if template_source.is_local_template:
            # Move the original directory down a level in the relative path
            # E.g. move ../../input_files/templates/cookiecutters/one to ../input_files/templates/cookiecutters/one
            expect_template_source_path = str(
                Path(*Path(template_source.path).parts[1:])
            )
        else:
            expect_template_source_path = template_source.path
    else:
        raise ValueError(f"unsupported add mode {add_mode}")

    _assert_template_sources_config_is_correct(
        template_sources_config_dir / "flexlate.json",
        version=template_source.default_version,
        name=template_source.name,
        url=template_source.url,
        path=expect_template_source_path,
        render_relative_root_in_output=template_source.render_relative_root_in_output,
        render_relative_root_in_template=template_source.render_relative_root_in_template,
    )
    _assert_applied_templates_config_is_correct(
        applied_config_dir / "flexlate.json",
        expect_applied_template_root=expect_applied_template_root,
        version=template_source.default_version,
        template_source_type=template_source.type,
        name=template_source.name,
        expect_add_mode=add_mode,
    )

    project_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(
        project_config_path, user=False, add_mode=add_mode
    )


@pytest.mark.parametrize("update_from_subdir", [False, True])
def test_update_project(
    update_from_subdir: bool,
    flexlates: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
    template_source_with_relative: TemplateSourceFixture,
):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed
    template_source = template_source_with_relative

    no_input = flexlates.type == FlexlateType.APP
    subdir = GENERATED_REPO_DIR / "subdir1" / "subdir2"
    subdir.mkdir(parents=True)

    def assert_root_template_output_is_correct(
        after_version_update: bool = False,
        after_data_update: bool = False,
        target_version: Optional[str] = None,
    ):
        _assert_root_template_output_is_correct(
            template_source,
            after_version_update,
            after_data_update,
            target_version=target_version,
        )

    def assert_subdir_template_output_is_correct(
        after_version_update: bool = False, after_data_update: bool = False
    ):
        version = (
            template_source.version_2
            if after_version_update
            else template_source.version_1
        )
        input_data = (
            template_source.update_input_data
            if after_data_update
            else template_source.input_data
        )
        at_config_path = (
            subdir
            / template_source.evaluated_render_relative_root_in_output_creator(
                input_data
            )
            / "flexlate.json"
        )
        _assert_project_files_are_correct(
            subdir,
            expect_data=input_data,
            version=version,
            template_source_type=template_source.type,
        )
        _assert_applied_templates_config_is_correct(
            at_config_path,
            expect_applied_template_root=template_source.expect_local_applied_template_path,
            expect_data=input_data,
            version=version,
            template_source_type=template_source.type,
            name=template_source.name,
        )
        _assert_template_sources_config_is_empty(at_config_path)

    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(
            template_source.path, target_version=template_source.version_1
        )
        # Add an output in the main directory
        fxt.apply_template_and_add(
            template_source.name, data=template_source.input_data, no_input=no_input
        )
        assert_root_template_output_is_correct(target_version=template_source.version_1)

        # Add an output of the same template source in a subdirectory
        with change_directory_to(subdir):
            fxt.apply_template_and_add(
                template_source.name, data=template_source.input_data, no_input=no_input
            )
            assert_subdir_template_output_is_correct()

        update_directory = subdir if update_from_subdir else GENERATED_REPO_DIR
        with change_directory_to(update_directory):
            # First update does nothing, because version is at target version
            # When using app, it will throw an error
            if flexlates.type == FlexlateType.APP:
                with pytest.raises(TriedToCommitButNoChangesException) as excinfo:
                    fxt.update(no_input=True)
                assert "update did not make any new changes" in str(excinfo.value)
            else:
                # When using CLI stub, it will throw a CLIRunnerException
                with pytest.raises(CLIRunnerException) as excinfo:
                    fxt.update(no_input=True)
                assert "update did not make any new changes" in str(excinfo.value)

            assert_root_template_output_is_correct(
                target_version=template_source.version_1
            )
            assert_subdir_template_output_is_correct()

            # Now update by just passing new data, should change the output
            # even though the version has not changed
            fxt.update(data=[template_source.update_input_data] * 2, no_input=no_input)
            assert_root_template_output_is_correct(
                after_data_update=True, target_version=template_source.version_1
            )
            assert_subdir_template_output_is_correct(after_data_update=True)

            # Now update the target version
            fxt.update_template_source_target_version(
                template_source.name, template_source.version_2
            )

            # Make changes to update local templates to new version (no-op for remote templates)
            template_source.version_migrate_func(template_source.url_or_absolute_path)

            # Now update should go to new version
            fxt.update(no_input=True)

    assert_root_template_output_is_correct(
        after_version_update=True,
        after_data_update=True,
        target_version=template_source.version_2,
    )
    assert_subdir_template_output_is_correct(
        after_version_update=True, after_data_update=True
    )

    project_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=False)


def _assert_root_template_output_is_correct(
    template_source: TemplateSourceFixture,
    after_version_update: bool = False,
    after_data_update: bool = False,
    target_version: Optional[str] = None,
    num_template_sources: int = 1,
    template_source_index: int = 0,
):
    version = (
        template_source.version_2 if after_version_update else template_source.version_1
    )
    input_data = (
        template_source.update_input_data
        if after_data_update
        else template_source.input_data
    )
    at_config_path = (
        GENERATED_REPO_DIR
        / template_source.evaluated_render_relative_root_in_output_creator(input_data)
        / "flexlate.json"
    )
    _assert_project_files_are_correct(
        expect_data=input_data,
        version=version,
        template_source_type=template_source.type,
    )
    _assert_config_is_correct(
        at_config_path=at_config_path,
        expect_applied_template_root=template_source.expect_local_applied_template_path,
        expect_data=input_data,
        version=version,
        target_version=target_version,
        template_source_type=template_source.type,
        name=template_source.name,
        url=template_source.url,
        path=template_source.path,
        render_relative_root_in_output=template_source.render_relative_root_in_output,
        render_relative_root_in_template=template_source.render_relative_root_in_template,
        num_template_sources=num_template_sources,
        template_source_index=template_source_index,
    )


def test_update_one_template(
    flexlates: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed
    no_input = flexlates.type == FlexlateType.APP

    non_update_template_source: TemplateSourceFixture = COOKIECUTTER_REMOTE_FIXTURE
    with template_source_with_temp_dir_if_local_template(
        COPIER_LOCAL_FIXTURE
    ) as template_source:
        with change_directory_to(GENERATED_REPO_DIR):
            fxt.init_project()
            # Add both template sources and outputs in the main directory at version 1
            for i, ts in enumerate([template_source, non_update_template_source]):
                fxt.add_template_source(ts.path, target_version=ts.version_1)
                fxt.apply_template_and_add(
                    ts.name, data=ts.input_data, no_input=no_input
                )
                num_template_sources = i + 1
                _assert_root_template_output_is_correct(
                    ts,
                    num_template_sources=num_template_sources,
                    template_source_index=i,
                    target_version=ts.version_1,
                )

            # First update does nothing, because version is at target version
            # When using app, it will throw an error
            if flexlates.type == FlexlateType.APP:
                with pytest.raises(TriedToCommitButNoChangesException) as excinfo:
                    fxt.update([template_source.name], no_input=True)
                assert "update did not make any new changes" in str(excinfo.value)
            else:
                # When using CLI stub, it will throw a CLIRunnerException
                with pytest.raises(CLIRunnerException) as excinfo:
                    fxt.update([template_source.name], no_input=True)
                assert "update did not make any new changes" in str(excinfo.value)

            _assert_root_template_output_is_correct(
                template_source,
                target_version=template_source.version_1,
                num_template_sources=2,
            )
            _assert_root_template_output_is_correct(
                non_update_template_source,
                template_source_index=1,
                target_version=non_update_template_source.version_1,
                num_template_sources=2,
            )

            # Now update by just passing new data, should change the output
            # even though the version has not changed
            fxt.update(
                [template_source.name],
                data=[template_source.update_input_data],
                no_input=no_input,
            )
            _assert_root_template_output_is_correct(
                template_source,
                after_data_update=True,
                target_version=template_source.version_1,
                num_template_sources=2,
            )
            # Other template unaffected
            _assert_root_template_output_is_correct(
                non_update_template_source,
                template_source_index=1,
                target_version=non_update_template_source.version_1,
                num_template_sources=2,
            )

            # Now update the target version
            fxt.update_template_source_target_version(
                template_source.name, template_source.version_2
            )

            # Make changes to update local templates to new version (no-op for remote templates)
            template_source.version_migrate_func(template_source.url_or_absolute_path)

            # Now update should go to new version
            fxt.update([template_source.name], no_input=True)

        _assert_root_template_output_is_correct(
            template_source,
            after_version_update=True,
            after_data_update=True,
            num_template_sources=2,
            target_version=template_source.version_2,
        )
        # Other template unaffected
        _assert_root_template_output_is_correct(
            non_update_template_source,
            template_source_index=1,
            num_template_sources=2,
            target_version=non_update_template_source.version_1,
        )

        project_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
        _assert_project_config_is_correct(project_config_path, user=False)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
@pytest.mark.parametrize("user", [False, True])
def test_remove_template_source(
    user: bool,
    flexlates: FlexlateFixture,
    add_mode: AddMode,
    subdir_style: SubdirStyle,
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    fxt = flexlates.flexlate
    config_root = (
        GENERATED_FILES_DIR if add_mode == AddMode.USER else GENERATED_REPO_DIR
    )
    project_config_root = GENERATED_FILES_DIR if user else GENERATED_REPO_DIR
    config_path = config_root / "flexlate.json"
    project_config_path = project_config_root / "flexlate-project.json"
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(user=user, default_add_mode=add_mode)
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        assert config_path.exists()
        fxt.remove_template_source(COOKIECUTTER_REMOTE_NAME)
        assert not config_path.exists()

    _assert_project_config_is_correct(project_config_path, user=user, add_mode=add_mode)

    # Works for main dir, now try subdir
    subdir = GENERATED_REPO_DIR / "subdir1" / "subdir2"
    subdir.mkdir(parents=True)
    subdir_config_root: Path
    if add_mode == AddMode.USER:
        subdir_config_root = GENERATED_FILES_DIR
    elif add_mode == AddMode.LOCAL:
        subdir_config_root = subdir
    elif add_mode == AddMode.PROJECT:
        subdir_config_root = GENERATED_REPO_DIR
    else:
        raise ValueError("unsupported add mode")
    subdir_config_path = subdir_config_root / "flexlate.json"

    if subdir_style == SubdirStyle.CD:
        with change_directory_to(subdir):
            fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
            assert subdir_config_path.exists()
            fxt.remove_template_source(COOKIECUTTER_REMOTE_NAME)
            assert not subdir_config_path.exists()
    elif subdir_style == SubdirStyle.PROVIDE_RELATIVE:
        out_root = subdir.relative_to(os.getcwd())
        fxt.add_template_source(
            COOKIECUTTER_REMOTE_URL,
            template_root=out_root,
        )
        assert subdir_config_path.exists()
        fxt.remove_template_source(COOKIECUTTER_REMOTE_NAME, template_root=out_root)
        assert not subdir_config_path.exists()
    elif subdir_style == SubdirStyle.PROVIDE_ABSOLUTE:
        out_root = subdir.absolute()
        fxt.add_template_source(
            COOKIECUTTER_REMOTE_URL,
            template_root=out_root,
        )
        assert subdir_config_path.exists()
        fxt.remove_template_source(COOKIECUTTER_REMOTE_NAME, template_root=out_root)
        assert not subdir_config_path.exists()

    _assert_project_config_is_correct(project_config_path, user=user, add_mode=add_mode)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
@pytest.mark.parametrize("user", [False, True])
def test_remove_applied_template(
    user: bool,
    flexlates: FlexlateFixture,
    add_mode: AddMode,
    subdir_style: SubdirStyle,
    repo_with_placeholder_committed: Repo,
):
    fxt = flexlates.flexlate
    no_input = flexlates.type == FlexlateType.APP
    config_root = (
        GENERATED_FILES_DIR if add_mode == AddMode.USER else GENERATED_REPO_DIR
    )
    project_config_root = GENERATED_FILES_DIR if user else GENERATED_REPO_DIR
    config_path = config_root / "flexlate.json"
    project_config_path = project_config_root / "flexlate-project.json"
    expect_data: CookiecutterRemoteTemplateData = dict(name="woo", key="it works")
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(user=user, default_add_mode=add_mode)
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(
            COOKIECUTTER_REMOTE_NAME, data=expect_data, no_input=no_input
        )
        _assert_project_files_are_correct(expect_data=expect_data)
        fxt.remove_applied_template_and_output(COOKIECUTTER_REMOTE_NAME)

        _assert_project_files_do_not_exist(expect_data=expect_data)
        _assert_project_config_is_correct(
            project_config_path, user=user, add_mode=add_mode
        )
        _assert_applied_templates_config_is_empty(config_path)

        # Works for main dir, now try subdir
        subdir = GENERATED_REPO_DIR / "subdir1" / "subdir2"
        subdir.mkdir(parents=True)
        if subdir_style == SubdirStyle.CD:
            with change_directory_to(subdir):
                fxt.apply_template_and_add(
                    COOKIECUTTER_REMOTE_NAME, data=expect_data, no_input=no_input
                )
                fxt.remove_applied_template_and_output(COOKIECUTTER_REMOTE_NAME)
        elif subdir_style == SubdirStyle.PROVIDE_RELATIVE:
            out_root = subdir.relative_to(os.getcwd())
            fxt.apply_template_and_add(
                COOKIECUTTER_REMOTE_NAME,
                data=expect_data,
                no_input=no_input,
                out_root=out_root,
            )
            fxt.remove_applied_template_and_output(
                COOKIECUTTER_REMOTE_NAME, out_root=out_root
            )
        elif subdir_style == SubdirStyle.PROVIDE_ABSOLUTE:
            out_root = subdir.absolute()
            fxt.apply_template_and_add(
                COOKIECUTTER_REMOTE_NAME,
                data=expect_data,
                no_input=no_input,
                out_root=out_root,
            )
            fxt.remove_applied_template_and_output(
                COOKIECUTTER_REMOTE_NAME, out_root=out_root
            )

    _assert_project_files_do_not_exist(subdir, expect_data=expect_data)
    _assert_project_config_is_correct(project_config_path, user=user, add_mode=add_mode)
    assert not (subdir / "flexlate.json").exists()


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_undo(
    flexlates: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)
        # Work in a subdirectory so that we can run all operations.
        # Commit a file so that the folder will persist and ensure that
        # the file is never removed
        subdir = GENERATED_REPO_DIR / "subdir"
        subdir.mkdir()
        subdir_placeholder_path = (subdir / "some-file.txt").resolve()
        subdir_placeholder_path.write_text("something")
        manual_commit_message = "Add a placeholder in a subdir"
        stage_and_commit_all(repo, manual_commit_message)
        # Add an operation that will be undone
        with change_directory_to(subdir):
            # One check being careful about the input files, just to make sure
            # something is happening
            fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)
            config_path = subdir / "abc" / "flexlate.json"
            _assert_project_files_are_correct(subdir)
            _assert_applied_templates_config_is_correct(
                config_path, expect_applied_template_root=Path("..")
            )
            fxt.undo()
            _assert_project_files_do_not_exist(subdir)
            assert not config_path.exists()
            assert subdir_placeholder_path.read_text() == "something"
            # Now check everything just to make sure it can be undone
            is_cli = flexlates.type == FlexlateType.CLI
            for operation in UNDOABLE_OPERATIONS:
                operation.operation(fxt, is_cli)
                fxt.undo(num_operations=operation.num_transactions)
                _assert_project_files_do_not_exist(subdir)
                assert not config_path.exists()
                assert subdir_placeholder_path.read_text() == "something"

    def assert_merged_commit_history_is_correct():
        assert_main_commit_message_matches(repo.commit().message, manual_commit_message)
        assert len(repo.commit().parents) == 1
        parent = repo.commit().parents[0]
        assert_main_commit_message_matches(parent.message, "Update flexlate templates")

    assert_merged_commit_history_is_correct()
    _assert_project_files_are_correct()
    _assert_config_is_correct(
        at_config_path=GENERATED_REPO_DIR / "abc" / "flexlate.json",
        expect_applied_template_root=Path(".."),
    )
    _assert_project_config_is_correct()

    merged_branch_name = get_flexlate_branch_name(repo, DEFAULT_MERGED_BRANCH_NAME)
    template_branch_name = get_flexlate_branch_name(repo, DEFAULT_TEMPLATE_BRANCH_NAME)

    for branch_name in [merged_branch_name, template_branch_name]:
        branch = repo.branches[branch_name]  # type: ignore
        branch.checkout()

    merged_branch = repo.branches[merged_branch_name]  # type: ignore
    merged_branch.checkout()
    assert_merged_commit_history_is_correct()

    template_branch = repo.branches[template_branch_name]  # type: ignore
    template_branch.checkout()

    assert_main_commit_message_matches(
        repo.commit().message, "Update flexlate templates"
    )
    assert len(repo.commit().parents) == 1
    parent = repo.commit().parents[0]
    assert_main_commit_message_matches(
        parent.message, "Applied template cookiecutter-simple-example to ."
    )


def test_init_project_from_template(
    flexlates: FlexlateFixture,
    template_source_with_relative: TemplateSourceFixture,
):
    fxt = flexlates.flexlate
    template_source = template_source_with_relative

    no_input = flexlates.type == FlexlateType.APP
    with change_directory_to(GENERATED_FILES_DIR):
        subdir = GENERATED_FILES_DIR / "subdir" / "nested"
        fxt.init_project_from(
            template_source.path,
            path=subdir,
            data=template_source.input_data,
            no_input=no_input,
        )

    relative_root = template_source.evaluated_render_relative_root_in_output_creator(
        template_source.input_data
    )
    root = subdir / relative_root
    project_files_check_root = subdir
    project_folder_name = relative_root.name
    if relative_root == Path("."):
        # When relative root is current directory, init-from creates a new folder
        # with name as passed. The default name is "project"
        project_folder_name = "project"
        root = root / project_folder_name
        project_files_check_root = project_files_check_root / project_folder_name

    _assert_project_files_are_correct(
        root=project_files_check_root,
        expect_data=template_source.input_data,
        template_source_type=template_source.type,
        version=template_source.default_version,
    )

    _assert_config_is_correct(
        at_config_path=root / "flexlate.json",
        ts_config_path=root / "flexlate.json",
        expect_applied_template_root=template_source.expect_local_applied_template_path,
        expect_data=template_source.input_data,
        template_source_type=template_source.type,
        version=template_source.default_version,
        name=template_source.name,
        url=template_source.url,
        path=template_source.relative_path_relative_to(root),
        render_relative_root_in_output=template_source.render_relative_root_in_output,
        render_relative_root_in_template=template_source.render_relative_root_in_template,
    )

    project_config_path = root / "flexlate-project.json"
    _assert_project_config_is_correct(
        project_config_path,
        user=False,
        project_folder_name=project_folder_name,
        project_containing_folder=subdir,
    )

    with change_directory_to(root):
        _assert_sync_is_a_no_op(flexlates)


def test_sync_manually_remove_applied_template(
    flexlates: FlexlateFixture, repo_with_placeholder_committed: Repo
):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed

    output_folder = GENERATED_REPO_DIR / "abc"

    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)

        assert output_folder.exists()
        shutil.rmtree(output_folder)
        stage_and_commit_all(repo, "Manual change to remove applied template")

        fxt.sync()

    merged_branch_name = get_flexlate_branch_name(repo, DEFAULT_MERGED_BRANCH_NAME)
    template_branch_name = get_flexlate_branch_name(repo, DEFAULT_TEMPLATE_BRANCH_NAME)

    for branch_name in [
        "master",
        merged_branch_name,
        template_branch_name,
    ]:
        branch: Head = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        assert not output_folder.exists()


def test_merge(flexlates: FlexlateFixture, repo_with_placeholder_committed: Repo):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed

    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        # Make a dummy change
        dummy_file = GENERATED_REPO_DIR / "something.txt"
        dummy_file.write_text("text")
        stage_and_commit_all(repo, "Add a dummy change to the main branch")
        with _checkout_new_branch_that_merges_back(repo, fxt, "add-source"):
            fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        with _checkout_new_branch_that_merges_back(repo, fxt, "add-template"):
            fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)

    for branch_name in ["master", DEFAULT_MERGED_BRANCH_NAME]:
        branch = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        _assert_project_files_are_correct()
        assert_main_commit_message_matches(
            "Merge branch 'flexlate-templates-add-template' into flexlate-output-add-template",
            repo.commit().message,
        )

    template_branch = repo.branches[DEFAULT_TEMPLATE_BRANCH_NAME]  # type: ignore
    template_branch.checkout()
    assert_main_commit_message_matches(
        "Update flexlate templates", repo.commit().message
    )


def test_push(flexlates: FlexlateFixture, repo_with_placeholder_committed: Repo):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed

    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        # Make a dummy change
        dummy_file = GENERATED_REPO_DIR / "something.txt"
        dummy_file.write_text("text")
        stage_and_commit_all(repo, "Add a dummy change to the main branch")
        with _checkout_new_branch_that_merges_back(repo, fxt, "add-source"):
            fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        with _checkout_new_branch_that_merges_back(
            repo, fxt, "add-template", delete=False
        ):
            fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)

        feature_merged_branch_name = get_flexlate_branch_name_for_feature_branch(
            "add-template", DEFAULT_MERGED_BRANCH_NAME
        )
        feature_template_branch_name = get_flexlate_branch_name_for_feature_branch(
            "add-template", DEFAULT_TEMPLATE_BRANCH_NAME
        )
        all_branches = [
            DEFAULT_TEMPLATE_BRANCH_NAME,
            DEFAULT_MERGED_BRANCH_NAME,
            feature_merged_branch_name,
            feature_template_branch_name,
        ]

        with add_local_remote_and_check_branches_on_exit(repo, all_branches):
            fxt.push_feature_flexlate_branches("add-template")
            fxt.push_main_flexlate_branches()


def test_check(
    flexlates_ignore_cli_exceptions: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
    capsys: CaptureFixture,
):
    flexlates = flexlates_ignore_cli_exceptions
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed
    template_source: TemplateSourceFixture = COPIER_REMOTE_FIXTURE

    def _run_check_and_asserter_on_output(
        stdout_asserter: Callable[[str], None], stderr_asserter: Callable[[str], None]
    ):
        # Clear the captured output
        capsys.readouterr()

        # Run the check with no names
        output = capture_output(flexlates, capsys, lambda fxt: fxt.check())

        stdout_asserter(output.stdout)
        stderr_asserter(output.stderr)

        # Run the same check passing the name
        output2 = capture_output(
            flexlates, capsys, lambda fxt: fxt.check(names=[template_source.name])
        )
        stdout_asserter(output2.stdout)
        stderr_asserter(output2.stderr)

    def _assert_no_output(output: str):
        assert not output

    def _assert_template_name_old_version_and_new_version_in_output(output: str):
        assert template_source.name in output
        # Version truncates in small or no terminal so just check for beginning
        assert template_source.version_1[:15] in output
        assert template_source.version_2[:15] in output
        assert "Run fxt update" in output

    def _assert_success_output(output: str):
        assert "up to date" in output
        assert not "Run fxt update" in output

    def assert_no_templates_need_to_be_updated():
        _run_check_and_asserter_on_output(_assert_success_output, _assert_no_output)

    def assert_template_needs_to_be_updated():
        _run_check_and_asserter_on_output(
            _assert_template_name_old_version_and_new_version_in_output,
            _assert_no_output,
        )

    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(
            template_source.path, target_version=template_source.version_1
        )

        assert_no_templates_need_to_be_updated()

        # Now update the target version
        fxt.update_template_source_target_version(
            template_source.name, template_source.version_2
        )

        # Make changes to update local templates to new version (no-op for remote templates)
        template_source.version_migrate_func(template_source.url_or_absolute_path)

        assert_template_needs_to_be_updated()


def test_bootstrap(
    flexlates: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
    template_source_with_relative: TemplateSourceFixture,
):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed
    template_source = template_source_with_relative
    no_input = flexlates.type == FlexlateType.APP

    with change_directory_to(GENERATED_REPO_DIR):
        template_source.render_without_flexlate()
        stage_and_commit_all(
            repo, f"Render files with {template_source.template_type.value}"
        )
        fxt.bootstrap_flexlate_init_from_existing_template(
            template_source.path,
            template_version=template_source.version_1,
            data=template_source.input_data,
            no_input=no_input,
        )

        _assert_root_template_output_is_correct(template_source)

        # Make changes to update local templates to new version (no-op for remote templates)
        template_source.version_migrate_func(template_source.url_or_absolute_path)

        # Should be anle to directly update after bootstrap
        fxt.update(data=[template_source.update_input_data], no_input=no_input)

        _assert_root_template_output_is_correct(
            template_source, after_version_update=True, after_data_update=True
        )


def test_update_target_version(
    flexlates: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
    template_source: TemplateSourceFixture,
):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed

    config_path = GENERATED_REPO_DIR / "flexlate.json"

    def assert_target_version_is(version: Optional[str]):
        config = FlexlateConfig.load(config_path)
        assert len(config.template_sources) == 1
        ts = config.template_sources[0]
        assert ts.target_version == version

    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(template_source.path)
        assert_target_version_is(None)
        fxt.update_template_source_target_version(
            template_source.name, target_version=template_source.version_2
        )
        assert_target_version_is(template_source.version_2)

    last_commit_message = f"Changed target version for template source {template_source.name} to {template_source.version_2}"

    assert_main_commit_message_matches(repo.commit().message, last_commit_message)


@contextlib.contextmanager
def _checkout_new_branch_that_merges_back(
    repo: Repo, fxt: Flexlate, branch_name: str, delete: bool = True
):
    checkout_new_branch(repo, branch_name)
    yield
    fxt.merge_flexlate_branches(delete=delete)
    checkout_existing_branch(repo, "master")
    merge_branch_into_current(repo, branch_name)


def _assert_project_files_are_correct(
    root: Path = GENERATED_REPO_DIR,
    expect_data: Optional[TemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
    template_source_type: TemplateSourceType = TemplateSourceType.COOKIECUTTER_REMOTE,
):
    default_data = _get_default_data(template_source_type)
    data: TemplateData = expect_data or default_data

    if template_source_type == TemplateSourceType.COOKIECUTTER_REMOTE:
        out_path = root / data["name"] / f"{data['name']}.txt"
        header = get_header_for_cookiecutter_remote_template(version)
        expect_content = f"{header}{data['key']}"
    elif template_source_type == TemplateSourceType.COPIER_REMOTE:
        out_path = root / f"{data['question1']}.txt"
        footer = get_footer_for_copier_remote_template(version)
        expect_content = f"{data['question2']}{footer}"
    elif template_source_type == TemplateSourceType.COOKIECUTTER_LOCAL:
        out_path = root / data["a"] / "text.txt"
        footer = get_footer_for_cookiecutter_local_template(version)
        expect_content = f"{data['a']}{data['c']}{footer}"
    elif template_source_type == TemplateSourceType.COPIER_LOCAL:
        out_path = root / f"{data['q1']}.txt"
        footer = get_footer_for_copier_local_template(version)
        expect_content = f"{data['q2']}{footer}"
    else:
        raise ValueError(f"unexpected template source type {template_source_type}")

    assert out_path.exists()
    content = out_path.read_text()
    assert content == expect_content


def _assert_project_files_do_not_exist(
    root: Path = GENERATED_REPO_DIR,
    expect_data: Optional[CookiecutterRemoteTemplateData] = None,
):
    data: CookiecutterRemoteTemplateData = expect_data or dict(name="abc", key="value")
    out_path = root / data["name"] / f"{data['name']}.txt"
    assert not out_path.exists()


def _assert_template_sources_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
    target_version: Optional[str] = None,
    name: str = COOKIECUTTER_REMOTE_NAME,
    url: str = COOKIECUTTER_REMOTE_URL,
    path: str = COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH,
    render_relative_root_in_output: Path = Path("."),
    render_relative_root_in_template: Path = Path("."),
    num_template_sources: int = 1,
    template_source_index: int = 0,
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Template source
    assert len(config.template_sources) == num_template_sources
    template_source = config.template_sources[template_source_index]
    assert template_source.name == name
    assert template_source.version == version
    assert template_source.target_version == target_version
    assert template_source.git_url == url
    assert template_source.path == path
    assert (
        template_source.render_relative_root_in_output == render_relative_root_in_output
    )
    assert (
        template_source.render_relative_root_in_template
        == render_relative_root_in_template
    )


def _assert_template_sources_config_is_empty(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 0


def _assert_applied_templates_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    expect_applied_template_root: Path = Path("."),
    expect_data: Optional[TemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
    template_source_type: TemplateSourceType = TemplateSourceType.COOKIECUTTER_REMOTE,
    name: str = COOKIECUTTER_REMOTE_NAME,
    expect_add_mode: AddMode = AddMode.LOCAL,
):
    data: TemplateData = expect_data or _get_default_data(template_source_type)
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Applied template
    assert len(config.applied_templates) == 1
    applied_template = config.applied_templates[0]
    assert applied_template.name == name
    assert applied_template.data == data
    assert applied_template.version == version
    assert applied_template.root == expect_applied_template_root
    assert applied_template.add_mode == expect_add_mode


def _assert_applied_templates_config_is_empty(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0


def _assert_config_is_correct(
    at_config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    ts_config_path: Optional[Path] = GENERATED_REPO_DIR / "flexlate.json",
    expect_applied_template_root: Path = Path("."),
    expect_data: Optional[CookiecutterRemoteTemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
    target_version: Optional[str] = None,
    template_source_type: TemplateSourceType = TemplateSourceType.COOKIECUTTER_REMOTE,
    name: str = COOKIECUTTER_REMOTE_NAME,
    url: str = COOKIECUTTER_REMOTE_URL,
    path: str = COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH,
    render_relative_root_in_output: Path = Path("{{ cookiecutter.name }}"),
    render_relative_root_in_template: Path = Path("{{ cookiecutter.name }}"),
    expect_add_mode: AddMode = AddMode.LOCAL,
    num_template_sources: int = 1,
    template_source_index: int = 0,
):
    _assert_applied_templates_config_is_correct(
        at_config_path,
        expect_applied_template_root,
        expect_data=expect_data,
        version=version,
        template_source_type=template_source_type,
        name=name,
        expect_add_mode=expect_add_mode,
    )
    _assert_template_sources_config_is_correct(
        ts_config_path,
        version=version,
        target_version=target_version,
        name=name,
        url=url,
        path=path,
        render_relative_root_in_output=render_relative_root_in_output,
        render_relative_root_in_template=render_relative_root_in_template,
        num_template_sources=num_template_sources,
        template_source_index=template_source_index,
    )


def _assert_project_config_is_correct(
    path: Path = GENERATED_REPO_DIR / "flexlate-project.json",
    user: bool = False,
    add_mode: AddMode = AddMode.LOCAL,
    project_folder_name: str = "project",
    project_containing_folder: Path = GENERATED_FILES_DIR,
):
    expect_project_path = project_containing_folder / project_folder_name
    project_config = FlexlateProjectConfig.load(path)
    assert len(project_config.projects) == 1
    project = project_config.projects[0]
    if user:
        assert project.path == project.path.absolute()
        assert project.path == expect_project_path
    else:
        assert project.path != project.path.absolute()
        assert (path.parent / project.path).absolute() == expect_project_path
    assert project.default_add_mode == add_mode


def _assert_sync_is_a_no_op(flexlate_fixture: FlexlateFixture):
    fxt = flexlate_fixture.flexlate
    if flexlate_fixture.type == FlexlateType.APP:
        with pytest.raises(UnnecessarySyncException):
            fxt.sync()
    else:
        with pytest.raises(CLIRunnerException) as exc_info:
            fxt.sync()
        assert "Everything is up to date" in str(exc_info.value)


def _get_default_data(template_source_type: TemplateSourceType) -> TemplateData:
    if template_source_type == TemplateSourceType.COOKIECUTTER_REMOTE:
        return dict(name="abc", key="value")
    elif template_source_type == TemplateSourceType.COPIER_REMOTE:
        return dict(question1="answer1", question2=2.7)
    elif template_source_type == TemplateSourceType.COOKIECUTTER_LOCAL:
        return dict(a="b", c="")
    elif template_source_type == TemplateSourceType.COPIER_LOCAL:
        return dict(q1="a1", q2=1, q3=None)
    else:
        raise ValueError(f"unexpected template source type {template_source_type}")
