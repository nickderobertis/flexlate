import os.path

from flexlate.main import Flexlate
from flexlate.template.copier import CopierTemplate
from flexlate.template.types import TemplateType
from tests.config import GENERATED_FILES_DIR
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


def test_init_from_current_path_cookiecutter(
    cookiecutter_one_template: CookiecutterTemplate,
):
    template = cookiecutter_one_template
    project_dir = GENERATED_FILES_DIR / "b"

    with change_directory_to(template.path):
        fxt.init_project_from(".", path=GENERATED_FILES_DIR, no_input=True)

    content_path = project_dir / "text.txt"
    content = content_path.read_text()
    assert content == "b"

    config_path = project_dir / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 1
    source = config.template_sources[0]
    assert source.name == template.name
    assert source.path == "../../input_files/templates/cookiecutters/one"
    assert source.version == template.version
    assert source.type == TemplateType.COOKIECUTTER
    assert source.render_relative_root_in_output == Path("{{ cookiecutter.a }}")
    assert source.render_relative_root_in_template == Path("{{ cookiecutter.a }}")
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"a": "b", "c": ""}
    assert at.root == Path("..")
    assert at.add_mode == AddMode.LOCAL


def test_init_from_current_path_copier(
    copier_one_template: CopierTemplate,
):
    template = copier_one_template
    project_dir = GENERATED_FILES_DIR / "project"

    with change_directory_to(template.path):
        fxt.init_project_from(".", path=GENERATED_FILES_DIR, no_input=True)

    content_path = project_dir / "a1.txt"
    content = content_path.read_text()
    assert content == "1"

    readme_path = project_dir / "README.md"
    assert readme_path.read_text() == "some existing content"

    config_path = project_dir / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 1
    source = config.template_sources[0]
    assert source.name == template.name
    assert source.path == "../../input_files/templates/copiers/one"
    assert source.version == template.version
    assert source.type == TemplateType.COPIER
    assert source.render_relative_root_in_output == Path(".")
    assert source.render_relative_root_in_template == Path(".")
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"q1": "a1", "q2": 1, "q3": None}
    assert at.root == Path(".")
    assert at.add_mode == AddMode.LOCAL
