# A bootstrap script to set up input files for config tests
from pathlib import Path

from flexlate.config import FlexlateConfig, TemplateSource, AppliedTemplateConfig
from tests.config import (
    COOKIECUTTER_ONE_DIR,
    CONFIGS_DIR,
    COOKIECUTTER_TWO_DIR,
    CONFIG_SUBDIR_2,
    PROJECT_DIR,
)


def create_config_1() -> FlexlateConfig:
    config = FlexlateConfig(
        template_sources=[
            TemplateSource(
                name="one", path=str(COOKIECUTTER_ONE_DIR.relative_to(PROJECT_DIR))
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
                name="two", path=str(COOKIECUTTER_TWO_DIR.relative_to(PROJECT_DIR))
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


if __name__ == "__main__":
    gen_configs()
