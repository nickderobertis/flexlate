# A bootstrap script to set up input files for config tests
import os
from pathlib import Path

from flexlate.add_mode import AddMode
from flexlate.config import (
    FlexlateConfig,
    TemplateSource,
    AppliedTemplateConfig,
    FlexlateProjectConfig,
    ProjectConfig,
)
from flexlate.template.types import TemplateType
from tests.config import (
    COOKIECUTTER_ONE_DIR,
    CONFIGS_DIR,
    COOKIECUTTER_TWO_DIR,
    CONFIG_SUBDIR_2,
    PROJECT_DIR,
    PROJECT_CONFIGS_PROJECT_2_PATH,
    PROJECT_CONFIGS_ROOT_DIR,
    PROJECT_CONFIGS_PROJECT_1_PATH,
    PROJECT_CONFIGS_PROJECT_1_SUBDIR,
    PROJECT_CONFIGS_PROJECT_2_SUBDIR,
    GENERATED_FILES_DIR,
)


def create_config_1() -> FlexlateConfig:
    config = FlexlateConfig(
        template_sources=[
            TemplateSource(
                name="one",
                path=str(os.path.relpath(COOKIECUTTER_ONE_DIR, GENERATED_FILES_DIR)),
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
    config.settings.custom_config_folder = CONFIGS_DIR
    return config


def create_config_2() -> FlexlateConfig:
    config = FlexlateConfig(
        template_sources=[
            TemplateSource(
                name="two",
                path=str(
                    os.path.relpath(
                        COOKIECUTTER_TWO_DIR, GENERATED_FILES_DIR / "subdir2"
                    )
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
    config.settings.custom_config_folder = CONFIG_SUBDIR_2
    return config


def gen_configs():
    config_1 = create_config_1()
    config_1.save()
    config_2 = create_config_2()
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
    config.settings.custom_config_folder = PROJECT_CONFIGS_ROOT_DIR
    return config


def create_project_config_1() -> FlexlateProjectConfig:
    config = FlexlateProjectConfig(projects=[ProjectConfig(path=Path("."))])
    config.settings.custom_config_folder = PROJECT_CONFIGS_PROJECT_1_PATH
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


if __name__ == "__main__":
    gen_configs()
    gen_project_configs()
