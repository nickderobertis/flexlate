# Integration tests
import os
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import appdirs
from git import GitCommandError

from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig, FlexlateProjectConfig
from tests.config import (
    GENERATED_FILES_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_VERSION_2,
    COOKIECUTTER_REMOTE_VERSION_1,
)
from tests.fixtures.git import *
from tests.fixtures.subdir_style import SubdirStyle, subdir_style
from tests.fixtures.template import (
    CookiecutterRemoteTemplateData,
    get_header_for_cookiecutter_remote_template,
)
from tests.fixtures.cli import FlexlateFixture, FlexlateType, flexlates
from tests.fixtures.add_mode import add_mode


def test_init_project_and_add_source_and_template(
    flexlates: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
):
    fxt = flexlates.flexlate
    no_input = flexlates.type == FlexlateType.APP
    repo = repo_with_placeholder_committed
    expect_data: CookiecutterRemoteTemplateData = dict(name="woo", key="it works")
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(
            COOKIECUTTER_REMOTE_NAME, data=expect_data, no_input=no_input
        )

    _assert_project_files_are_correct(expect_data=expect_data)
    _assert_config_is_correct(expect_data=expect_data)

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

    config_root = (
        GENERATED_FILES_DIR if add_mode == AddMode.USER else GENERATED_REPO_DIR
    )
    template_root = GENERATED_REPO_DIR if add_mode == AddMode.USER else Path(".")

    _assert_config_is_correct(
        config_root / "flexlate.json",
        expect_applied_template_root=template_root,
    )

    project_config_path = GENERATED_FILES_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=True, add_mode=add_mode)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_init_project_and_add_source_and_template_in_subdir(
    flexlates: FlexlateFixture,
    add_mode: AddMode,
    subdir_style: SubdirStyle,
    repo_with_placeholder_committed: Repo,
):
    fxt = flexlates.flexlate
    repo = repo_with_placeholder_committed
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(default_add_mode=add_mode)
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        subdir = GENERATED_REPO_DIR / "subdir"
        subdir.mkdir()
        if subdir_style == SubdirStyle.CD:
            with change_directory_to(subdir):
                fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)
        elif subdir_style == SubdirStyle.PROVIDE_RELATIVE:
            fxt.apply_template_and_add(
                COOKIECUTTER_REMOTE_NAME,
                no_input=True,
                out_root=subdir.relative_to(os.getcwd()),
            )
        elif subdir_style == SubdirStyle.PROVIDE_ABSOLUTE:
            fxt.apply_template_and_add(
                COOKIECUTTER_REMOTE_NAME, no_input=True, out_root=subdir.absolute()
            )

    _assert_project_files_are_correct(GENERATED_REPO_DIR / "subdir")

    if add_mode == AddMode.LOCAL:
        applied_config_dir = GENERATED_REPO_DIR / "subdir"
        expect_applied_template_root = Path(".")
        template_sources_config_dir = GENERATED_REPO_DIR
    elif add_mode == AddMode.PROJECT:
        applied_config_dir = GENERATED_REPO_DIR
        expect_applied_template_root = Path("subdir")
        template_sources_config_dir = GENERATED_REPO_DIR
    elif add_mode == AddMode.USER:
        applied_config_dir = GENERATED_FILES_DIR
        expect_applied_template_root = (GENERATED_REPO_DIR / Path("subdir")).absolute()
        template_sources_config_dir = GENERATED_FILES_DIR
    else:
        raise ValueError(f"unsupported add mode {add_mode}")

    _assert_template_sources_config_is_correct(
        template_sources_config_dir / "flexlate.json"
    )
    _assert_applied_templates_config_is_correct(
        applied_config_dir / "flexlate.json",
        expect_applied_template_root=expect_applied_template_root,
    )

    project_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(
        project_config_path, user=False, add_mode=add_mode
    )


def test_update_project(
    flexlates: FlexlateFixture,
    repo_with_placeholder_committed: Repo,
):
    fxt = flexlates.flexlate
    no_input = flexlates.type == FlexlateType.APP
    repo = repo_with_placeholder_committed
    expect_data: CookiecutterRemoteTemplateData = dict(name="woo", key="it works")
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(
            COOKIECUTTER_REMOTE_URL, target_version=COOKIECUTTER_REMOTE_VERSION_1
        )
        fxt.apply_template_and_add(
            COOKIECUTTER_REMOTE_NAME, data=expect_data, no_input=no_input
        )
        _assert_project_files_are_correct(
            expect_data=expect_data, version=COOKIECUTTER_REMOTE_VERSION_1
        )
        _assert_config_is_correct(
            expect_data=expect_data, version=COOKIECUTTER_REMOTE_VERSION_1
        )

        # First update does nothing, because version is at target version
        # When using app, it will throw an error
        if flexlates.type == FlexlateType.APP:
            with pytest.raises(GitCommandError) as excinfo:
                fxt.update(no_input=True)
            assert "Your branch is up to date" in str(excinfo.value)
        else:
            # When using CLI, it will not throw an error, just display the message
            fxt.update(no_input=True)

        _assert_project_files_are_correct(
            expect_data=expect_data, version=COOKIECUTTER_REMOTE_VERSION_1
        )
        _assert_config_is_correct(
            expect_data=expect_data, version=COOKIECUTTER_REMOTE_VERSION_1
        )

        # Now update the target version
        # TODO: replace with cli command to update target version once it exists
        config_path = GENERATED_REPO_DIR / "flexlate.json"
        config = FlexlateConfig.load(config_path)
        source = config.template_sources[0]
        source.target_version = COOKIECUTTER_REMOTE_VERSION_2
        config.save()
        stage_and_commit_all(
            repo, "Update target version for cookiecutter to version 2"
        )
        # Now update should go to new version
        fxt.update(no_input=True)

    _assert_project_files_are_correct(expect_data=expect_data)
    _assert_config_is_correct(expect_data=expect_data)

    project_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=False)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
@pytest.mark.parametrize("user", [False, True])
def test_remove_template_source(
    user: bool,
    flexlates: FlexlateFixture,
    add_mode: AddMode,
    repo_with_placeholder_committed: Repo,
):
    fxt = flexlates.flexlate
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(user=user, default_add_mode=add_mode)
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.remove_template_source(COOKIECUTTER_REMOTE_NAME)

    config_root = (
        GENERATED_FILES_DIR if add_mode == AddMode.USER else GENERATED_REPO_DIR
    )
    project_config_root = GENERATED_FILES_DIR if user else GENERATED_REPO_DIR

    _assert_template_sources_config_is_empty(config_root / "flexlate.json")
    project_config_path = project_config_root / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=user, add_mode=add_mode)


def _assert_project_files_are_correct(
    root: Path = GENERATED_REPO_DIR,
    expect_data: Optional[CookiecutterRemoteTemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
):
    data: CookiecutterRemoteTemplateData = expect_data or dict(name="abc", key="value")
    header = get_header_for_cookiecutter_remote_template(version)
    out_path = root / data["name"] / f"{data['name']}.txt"
    assert out_path.exists()
    content = out_path.read_text()
    assert content == f"{header}{data['key']}"


def _assert_template_sources_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Template source
    assert len(config.template_sources) == 1
    template_source = config.template_sources[0]
    assert template_source.name == COOKIECUTTER_REMOTE_NAME
    assert template_source.version == version
    assert template_source.git_url == COOKIECUTTER_REMOTE_URL


def _assert_template_sources_config_is_empty(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 0


def _assert_applied_templates_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    expect_applied_template_root: Path = Path("."),
    expect_data: Optional[CookiecutterRemoteTemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
):
    data: CookiecutterRemoteTemplateData = expect_data or {
        "name": "abc",
        "key": "value",
    }
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Applied template
    assert len(config.applied_templates) == 1
    applied_template = config.applied_templates[0]
    assert applied_template.name == COOKIECUTTER_REMOTE_NAME
    assert applied_template.data == data
    assert applied_template.version == version
    assert applied_template.root == expect_applied_template_root


def _assert_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    expect_applied_template_root: Path = Path("."),
    expect_data: Optional[CookiecutterRemoteTemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
):
    _assert_applied_templates_config_is_correct(
        config_path,
        expect_applied_template_root,
        expect_data=expect_data,
        version=version,
    )
    _assert_template_sources_config_is_correct(config_path, version=version)


def _assert_project_config_is_correct(
    path: Path, user: bool = False, add_mode: AddMode = AddMode.LOCAL
):
    project_config = FlexlateProjectConfig.load(path)
    assert len(project_config.projects) == 1
    project = project_config.projects[0]
    if user:
        assert project.path == project.path.absolute()
        assert project.path == GENERATED_REPO_DIR
    else:
        assert project.path != project.path.absolute()
        assert (path.parent / project.path).absolute() == GENERATED_REPO_DIR
    assert project.default_add_mode == add_mode
