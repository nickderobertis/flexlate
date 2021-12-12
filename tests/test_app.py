# Integration tests
import os
from pathlib import Path
from unittest.mock import patch

import appdirs

from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig, FlexlateProjectConfig
from flexlate.main import Flexlate
from tests.config import (
    GENERATED_FILES_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_VERSION_2,
    GENERATED_REPO_DIR,
)
from tests.dirutils import change_directory_to
from tests.fixtures.git import *


def test_init_project_and_add_source_and_template(
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    fxt = Flexlate()
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)

    _assert_project_files_are_correct()
    _assert_config_is_correct()

    project_config_path = GENERATED_REPO_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=False)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_init_project_for_user_and_add_source_and_template(
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    fxt = Flexlate()
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(user=True)
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)
    _assert_project_files_are_correct()
    _assert_config_is_correct()

    project_config_path = GENERATED_FILES_DIR / "flexlate-project.json"
    _assert_project_config_is_correct(project_config_path, user=True)


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
@pytest.mark.parametrize("add_mode", [AddMode.LOCAL, AddMode.PROJECT, AddMode.USER])
def test_init_project_for_user_and_add_source_and_template(
    add_mode: AddMode,
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    fxt = Flexlate()
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
@pytest.mark.parametrize("add_mode", [AddMode.LOCAL, AddMode.PROJECT, AddMode.USER])
def test_init_project_and_add_source_and_template_in_subdir(
    add_mode: AddMode,
    repo_with_placeholder_committed: Repo,
):
    repo = repo_with_placeholder_committed
    fxt = Flexlate()
    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project(default_add_mode=add_mode)
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        subdir = GENERATED_REPO_DIR / "subdir"
        subdir.mkdir()
        with change_directory_to(subdir):
            fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)

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


def _assert_project_files_are_correct(root: Path = GENERATED_REPO_DIR):
    out_path = root / "abc" / "abc.txt"
    assert out_path.exists()
    content = out_path.read_text()
    assert content == "some new header\nvalue"


def _assert_template_sources_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Template source
    assert len(config.template_sources) == 1
    template_source = config.template_sources[0]
    assert template_source.name == COOKIECUTTER_REMOTE_NAME
    assert template_source.version == COOKIECUTTER_REMOTE_VERSION_2
    assert template_source.git_url == COOKIECUTTER_REMOTE_URL


def _assert_applied_templates_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    expect_applied_template_root: Path = Path("."),
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Applied template
    assert len(config.applied_templates) == 1
    applied_template = config.applied_templates[0]
    assert applied_template.name == COOKIECUTTER_REMOTE_NAME
    assert applied_template.data == {"name": "abc", "key": "value"}
    assert applied_template.version == COOKIECUTTER_REMOTE_VERSION_2
    assert applied_template.root == expect_applied_template_root


def _assert_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    expect_applied_template_root: Path = Path("."),
):
    _assert_applied_templates_config_is_correct(
        config_path, expect_applied_template_root
    )
    _assert_template_sources_config_is_correct(config_path)


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
