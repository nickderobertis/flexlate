from pathlib import Path

from flexlate.config_manager import ConfigManager
from tests.config import CONFIGS_DIR


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
