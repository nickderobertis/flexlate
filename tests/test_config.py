import os.path
from pathlib import Path

from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig, AppliedTemplateConfig, FlexlateProjectConfig
from flexlate.config_manager import ConfigManager
from flexlate.exc import FlexlateProjectConfigFileNotExistsException
from flexlate.update.main import Updater
from flexlate.update.template import TemplateUpdate
from tests.config import (
    CONFIGS_DIR,
    GENERATED_FILES_DIR,
    PROJECT_CONFIGS_PROJECT_1_PATH,
    PROJECT_CONFIGS_PROJECT_1_SUBDIR,
    PROJECT_CONFIGS_PROJECT_2_PATH,
    PROJECT_CONFIGS_PROJECT_2_SUBDIR,
    PROJECT_CONFIGS_DIR,
    GENERATED_REPO_DIR,
)
from tests.dirutils import wipe_generated_folder
from tests.fixtures.config import generated_dir_with_configs
from tests.fixtures.template import *


def test_load_multi_config():
    manager = ConfigManager()
    config = manager.load_config(CONFIGS_DIR)
    assert len(config.template_sources) == 2
    source_one, source_two = config.template_sources
    assert source_one.name == "one"
    assert source_two.name == "two"
    assert len(config.applied_templates) == 4
    roots = [str(applied.root) for applied in config.applied_templates]
    assert roots == [".", "subdir1", "subdir2", str(Path("subdir2") / "subdir2_2")]


def test_update_and_save_multi_config(
    generated_dir_with_configs: None,
    cookiecutter_one_modified_template: CookiecutterTemplate,
):
    manager = ConfigManager()
    updater = Updater()
    template_updates = updater.get_updates_for_templates(
        [cookiecutter_one_modified_template],
        [{"a": "yeah", "c": "woo"}],
        project_root=GENERATED_FILES_DIR,
        config_manager=manager,
    )
    manager.update_templates(
        template_updates,
        project_root=GENERATED_FILES_DIR,
    )

    config_1_path = GENERATED_FILES_DIR / "flexlate.json"
    config_2_path = GENERATED_FILES_DIR / "subdir2" / "flexlate.json"
    config_1 = FlexlateConfig.load(config_1_path)
    config_2 = FlexlateConfig.load(config_2_path)

    def assert_is_updated_template_one(template: AppliedTemplateConfig):
        assert template.name == "one"
        assert template.version == COOKIECUTTER_ONE_MODIFIED_VERSION
        assert template.data["a"] == "yeah"
        assert template.data["c"] == "woo"

    def assert_is_original_template_two(template: AppliedTemplateConfig):
        assert template.name == "two"
        assert template.version == "some version"
        assert template.data["a"] == "b"
        assert template.data["d"] == "e"

    assert len(config_1.applied_templates) == 2
    assert_is_updated_template_one(config_1.applied_templates[0])
    assert_is_updated_template_one(config_1.applied_templates[1])
    assert config_1.applied_templates[0].root == Path(".")
    assert config_1.applied_templates[1].root == Path("subdir1")
    assert config_1.applied_templates[0].add_mode == AddMode.LOCAL
    assert config_1.applied_templates[1].add_mode == AddMode.PROJECT

    assert len(config_2.applied_templates) == 2
    assert_is_original_template_two(config_2.applied_templates[0])
    assert_is_updated_template_one(config_2.applied_templates[1])
    assert config_2.applied_templates[0].root == Path(".")
    assert config_2.applied_templates[1].root == Path("subdir2_2")
    assert config_2.applied_templates[0].add_mode == AddMode.LOCAL
    assert config_2.applied_templates[1].add_mode == AddMode.LOCAL


@pytest.mark.parametrize("add_mode", [AddMode.LOCAL, AddMode.PROJECT, AddMode.USER])
def test_add_project_config_in_project(add_mode: AddMode):
    wipe_generated_folder()
    manager = ConfigManager()
    manager.add_project(GENERATED_FILES_DIR, default_add_mode=add_mode)
    config = FlexlateProjectConfig.load(GENERATED_FILES_DIR / "flexlate-project.json")
    assert len(config.projects) == 1
    project = config.projects[0]
    assert project.path == Path(".")
    assert project.default_add_mode == add_mode


# TODO: Test add project in user config
#  It is a bit difficult because will need to mock config to set location


@pytest.mark.parametrize(
    "path", [PROJECT_CONFIGS_PROJECT_1_SUBDIR, PROJECT_CONFIGS_PROJECT_1_PATH]
)
def test_load_local_project_config(path: Path):
    manager = ConfigManager()
    config = manager.load_project_config(path)
    assert config.path == PROJECT_CONFIGS_PROJECT_1_PATH
    assert config.default_add_mode == AddMode.LOCAL


@pytest.mark.parametrize(
    "path", [PROJECT_CONFIGS_PROJECT_2_SUBDIR, PROJECT_CONFIGS_PROJECT_2_PATH]
)
def test_load_recursive_project_config(path: Path):
    manager = ConfigManager()
    config = manager.load_project_config(path)
    assert config.path == PROJECT_CONFIGS_PROJECT_2_PATH
    assert config.default_add_mode == AddMode.LOCAL


def test_fail_to_load_non_existent_project_config():
    # TODO: Figure out how to isolate no project config test
    #  It would currently fail if the developer happens to be using flexlate in a parent directory
    manager = ConfigManager()
    with pytest.raises(FlexlateProjectConfigFileNotExistsException):
        config = manager.load_project_config(PROJECT_CONFIGS_DIR)
