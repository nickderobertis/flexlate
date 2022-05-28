# A bootstrap script to set up input files for config tests
import os
from pathlib import Path
from typing import Optional

from flexlate.add_mode import AddMode
from flexlate.config import (
    AppliedTemplateConfig,
    FlexlateConfig,
    FlexlateProjectConfig,
    ProjectConfig,
    TemplateSource,
)
from flexlate.template.types import TemplateType
from tests import config as test_config
from tests.config import (
    CONFIG_SUBDIR_2,
    CONFIGS_DIR,
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_TWO_DIR,
    PROJECT_CONFIGS_PROJECT_1_PATH,
    PROJECT_CONFIGS_PROJECT_1_SUBDIR,
    PROJECT_CONFIGS_PROJECT_2_PATH,
    PROJECT_CONFIGS_PROJECT_2_SUBDIR,
    PROJECT_CONFIGS_ROOT_DIR,
    PROJECT_DIR,
)


def create_config_1(
    location: Optional[Path] = None, relative_to: Optional[Path] = None
) -> FlexlateConfig:
    relative_to = relative_to or test_config.GENERATED_FILES_DIR
    location = location or CONFIGS_DIR
    config = FlexlateConfig(
        template_sources=[
            TemplateSource(
                name="one",
                path=str(os.path.relpath(COOKIECUTTER_ONE_DIR, relative_to)),
                type=TemplateType.COOKIECUTTER,
                render_relative_root_in_output=Path("{{ cookiecutter.a }}"),
                render_relative_root_in_template=Path("{{ cookiecutter.a }}"),
            ),
        ],
        applied_templates=[
            AppliedTemplateConfig(
                name="one",
                data=dict(a="b", c=""),
                version="d512c7e14e83cb4bc8d4e5ae06bb357e",
                add_mode=AddMode.LOCAL,
            ),
            AppliedTemplateConfig(
                name="one",
                data=dict(a="b", c=""),
                version="d512c7e14e83cb4bc8d4e5ae06bb357e",
                root=Path("subdir1"),
                add_mode=AddMode.PROJECT,
            ),
        ],
    )
    config.settings = FlexlateConfig._settings_with_overrides(
        custom_config_folder=location
    )
    return config


def create_config_2(
    location: Optional[Path] = None, relative_to: Optional[Path] = None
) -> FlexlateConfig:
    relative_to = relative_to or test_config.GENERATED_FILES_DIR
    location = location or CONFIGS_DIR
    config = FlexlateConfig(
        template_sources=[
            TemplateSource(
                name="two",
                path=str(
                    os.path.relpath(COOKIECUTTER_TWO_DIR, relative_to / "subdir2")
                ),
                type=TemplateType.COOKIECUTTER,
                render_relative_root_in_output=Path("{{ cookiecutter.a }}"),
                render_relative_root_in_template=Path("{{ cookiecutter.a }}"),
            ),
        ],
        applied_templates=[
            AppliedTemplateConfig(
                name="two",
                data=dict(a="b", d="e"),
                version="some version",
                add_mode=AddMode.LOCAL,
            ),
            AppliedTemplateConfig(
                name="one",
                data=dict(a="b", c="something"),
                version="d512c7e14e83cb4bc8d4e5ae06bb357e",
                root=Path("subdir2_2"),
                add_mode=AddMode.LOCAL,
            ),
        ],
    )
    config.settings = FlexlateConfig._settings_with_overrides(
        custom_config_folder=location / "subdir2"
    )
    return config


def gen_configs(location: Optional[Path] = None, relative_to: Optional[Path] = None):
    config_1 = create_config_1(location, relative_to)
    config_1.save()
    config_2 = create_config_2(location, relative_to)
    config_2.save()


def create_project_config_root() -> FlexlateProjectConfig:
    config = FlexlateProjectConfig(
        projects=[
            ProjectConfig(
                path=PROJECT_CONFIGS_PROJECT_2_PATH.relative_to(
                    PROJECT_CONFIGS_ROOT_DIR
                )
            )
        ]
    )
    config.settings = FlexlateProjectConfig._settings_with_overrides(
        custom_config_folder=PROJECT_CONFIGS_ROOT_DIR
    )
    return config


def create_project_config_1() -> FlexlateProjectConfig:
    config = FlexlateProjectConfig(projects=[ProjectConfig(path=Path("."))])
    config.settings = FlexlateProjectConfig._settings_with_overrides(
        custom_config_folder=PROJECT_CONFIGS_PROJECT_1_PATH
    )
    return config


def gen_project_configs():
    if not PROJECT_CONFIGS_PROJECT_1_SUBDIR.exists():
        PROJECT_CONFIGS_PROJECT_1_SUBDIR.mkdir(parents=True)
    if not PROJECT_CONFIGS_PROJECT_2_SUBDIR.exists():
        PROJECT_CONFIGS_PROJECT_2_SUBDIR.mkdir(parents=True)
    config_root = create_project_config_root()
    config_root.save()
    config_1 = create_project_config_1()
    config_1.save()


def main(location: Optional[Path] = None, relative_to: Optional[Path] = None):
    gen_configs(location, relative_to)
    gen_project_configs()


if __name__ == "__main__":
    main()
