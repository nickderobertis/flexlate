import os
from pathlib import Path

from flexlate.config import FlexlateConfig

# NOTE: currently unused, consider removing
def patch_config_location(config: FlexlateConfig, new_folder: Path):
    orig_project_root = os.path.commonpath(
        [conf.settings.config_location for conf in config.child_configs]
    )
    config.settings.custom_config_folder = new_folder
    for child_config in config.child_configs:
        orig_child_folder = child_config.settings.config_location.parent
        orig_relative_folder = orig_child_folder.relative_to(orig_project_root)
        new_relative_folder = new_folder / orig_relative_folder
        child_config.settings.custom_config_folder = new_relative_folder
