import os.path
from pathlib import Path

from flexlate.config import FlexlateConfig, AppliedTemplateConfig
from flexlate.config_manager import ConfigManager
from tests.config import CONFIGS_DIR, GENERATED_FILES_DIR
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
    manager.update_applied_templates(
        [cookiecutter_one_modified_template],
        [{"a": "yeah", "c": "woo"}],
        project_root=GENERATED_FILES_DIR,
    )

    config_1_path = GENERATED_FILES_DIR / "flexlate.json"
    config_2_path = GENERATED_FILES_DIR / "subdir2" / "flexlate.json"
    config_1 = FlexlateConfig.load(config_1_path)
    config_2 = FlexlateConfig.load(config_2_path)

    def assert_is_updated_template_one(template: AppliedTemplateConfig):
        assert template.name == "one"
        assert template.version == "7e18a6cc14856c8558ac999efa01e5e8"
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
    assert config_1.applied_templates[1].root == Path("subdir1")

    assert len(config_2.applied_templates) == 2
    assert_is_original_template_two(config_2.applied_templates[0])
    assert_is_updated_template_one(config_2.applied_templates[1])
    assert config_2.applied_templates[1].root == Path("subdir2/subdir2_2")
