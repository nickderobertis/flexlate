import os.path

from flexlate.main import Flexlate
from flexlate.template.types import TemplateType
from tests.fixtures.templated_repo import *

fxt = Flexlate()


def test_add_template_source_from_current_path(
    repo_with_placeholder_committed: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
):
    template = cookiecutter_one_template

    with change_directory_to(GENERATED_REPO_DIR):
        fxt.init_project()
        with change_directory_to(COOKIECUTTER_ONE_DIR):
            fxt.add_template_source(".", template_root=GENERATED_REPO_DIR)

    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0
    assert len(config.template_sources) == 1
    source = config.template_sources[0]
    assert source.name == template.name
    assert source.path == os.path.relpath(COOKIECUTTER_ONE_DIR, GENERATED_REPO_DIR)
    assert source.version == template.version
    assert source.type == TemplateType.COOKIECUTTER
    assert source.render_relative_root_in_output == Path("{{ cookiecutter.a }}")
    assert source.render_relative_root_in_template == Path("{{ cookiecutter.a }}")
