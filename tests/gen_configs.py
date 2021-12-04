# A bootstrap script to set up input files for config tests
from pathlib import Path

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
    PROJECT_CONFIGS_PROJECT_1_PATH, PROJECT_CONFIGS_PROJECT_1_SUBDIR, PROJECT_CONFIGS_PROJECT_2_SUBDIR,
)


def create_config_1() -> FlexlateConfig:
    config = FlexlateConfig(
        template_sources=[
            TemplateSource(
                name="one",
                path=str(COOKIECUTTER_ONE_DIR.relative_to(PROJECT_DIR)),
                type=TemplateType.COOKIECUTTER,
            ),
        ],
        applied_templates=[
            AppliedTemplateConfig(
                name="one",
                data=dict(a="b", c=""),
                version="d512c7e14e83cb4bc8d4e5ae06bb357e",
            ),
            AppliedTemplateConfig(
                name="one",
                data=dict(a="b", c=""),
                version="d512c7e14e83cb4bc8d4e5ae06bb357e",
                root=Path("subdir1"),
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
                path=str(COOKIECUTTER_TWO_DIR.relative_to(PROJECT_DIR)),
                type=TemplateType.COOKIECUTTER,
            ),
        ],
        applied_templates=[
            AppliedTemplateConfig(
                name="two",
                data=dict(a="b", d="e"),
                version="some version",
            ),
            AppliedTemplateConfig(
                name="one",
                data=dict(a="b", c="something"),
                version="d512c7e14e83cb4bc8d4e5ae06bb357e",
                root=Path("subdir2_2"),
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
