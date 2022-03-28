from pathlib import Path
from typing import Optional

from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig, FlexlateProjectConfig
from flexlate.template_data import TemplateData
from tests.config import (
    GENERATED_REPO_DIR,
    COOKIECUTTER_REMOTE_VERSION_2,
    COOKIECUTTER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_URL,
    GENERATED_FILES_DIR,
)
from tests.fixtures.template import (
    get_header_for_cookiecutter_remote_template,
    get_footer_for_copier_remote_template,
    get_footer_for_cookiecutter_local_template,
    get_footer_for_copier_local_template,
    CookiecutterRemoteTemplateData,
)
from tests.integration.fixtures.template_source import (
    TemplateSourceType,
    COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH,
    TemplateSourceFixture,
)


def assert_project_files_are_correct(
    root: Path = GENERATED_REPO_DIR,
    expect_data: Optional[TemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
    template_source_type: TemplateSourceType = TemplateSourceType.COOKIECUTTER_REMOTE,
):
    default_data = _get_default_data(template_source_type)
    data: TemplateData = expect_data or default_data

    if template_source_type == TemplateSourceType.COOKIECUTTER_REMOTE:
        out_path = root / data["name"] / f"{data['name']}.txt"
        header = get_header_for_cookiecutter_remote_template(version)
        expect_content = f"{header}{data['key']}"
    elif template_source_type == TemplateSourceType.COPIER_REMOTE:
        out_path = root / f"{data['question1']}.txt"
        footer = get_footer_for_copier_remote_template(version)
        expect_content = f"{data['question2']}{footer}"
    elif template_source_type == TemplateSourceType.COOKIECUTTER_LOCAL:
        out_path = root / data["a"] / "text.txt"
        footer = get_footer_for_cookiecutter_local_template(version)
        expect_content = f"{data['a']}{data['c']}{footer}"
    elif template_source_type == TemplateSourceType.COPIER_LOCAL:
        out_path = root / f"{data['q1']}.txt"
        footer = get_footer_for_copier_local_template(version)
        expect_content = f"{data['q2']}{footer}"
    else:
        raise ValueError(f"unexpected template source type {template_source_type}")

    assert out_path.exists()
    content = out_path.read_text()
    assert content == expect_content


def assert_project_files_do_not_exist(
    root: Path = GENERATED_REPO_DIR,
    expect_data: Optional[CookiecutterRemoteTemplateData] = None,
):
    data: CookiecutterRemoteTemplateData = expect_data or dict(name="abc", key="value")
    out_path = root / data["name"] / f"{data['name']}.txt"
    assert not out_path.exists()


def assert_template_sources_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
    target_version: Optional[str] = None,
    name: str = COOKIECUTTER_REMOTE_NAME,
    url: str = COOKIECUTTER_REMOTE_URL,
    path: str = COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH,
    render_relative_root_in_output: Path = Path("."),
    render_relative_root_in_template: Path = Path("."),
    num_template_sources: int = 1,
    template_source_index: int = 0,
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Template source
    assert len(config.template_sources) == num_template_sources
    template_source = config.template_sources[template_source_index]
    assert template_source.name == name
    assert template_source.version == version
    assert template_source.target_version == target_version
    assert template_source.git_url == url
    assert template_source.path == path
    assert (
        template_source.render_relative_root_in_output == render_relative_root_in_output
    )
    assert (
        template_source.render_relative_root_in_template
        == render_relative_root_in_template
    )


def assert_template_sources_config_is_empty(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.template_sources) == 0


def assert_applied_templates_config_is_correct(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    expect_applied_template_root: Path = Path("."),
    expect_data: Optional[TemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
    template_source_type: TemplateSourceType = TemplateSourceType.COOKIECUTTER_REMOTE,
    name: str = COOKIECUTTER_REMOTE_NAME,
    expect_add_mode: AddMode = AddMode.LOCAL,
):
    data: TemplateData = expect_data or _get_default_data(template_source_type)
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    # Applied template
    assert len(config.applied_templates) == 1
    applied_template = config.applied_templates[0]
    assert applied_template.name == name
    assert applied_template.data == data
    assert applied_template.version == version
    assert applied_template.root == expect_applied_template_root
    assert applied_template.add_mode == expect_add_mode


def assert_applied_templates_config_is_empty(
    config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
):
    assert config_path.exists()
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0


def assert_config_is_correct(
    at_config_path: Path = GENERATED_REPO_DIR / "flexlate.json",
    ts_config_path: Optional[Path] = GENERATED_REPO_DIR / "flexlate.json",
    expect_applied_template_root: Path = Path("."),
    expect_data: Optional[CookiecutterRemoteTemplateData] = None,
    version: str = COOKIECUTTER_REMOTE_VERSION_2,
    target_version: Optional[str] = None,
    template_source_type: TemplateSourceType = TemplateSourceType.COOKIECUTTER_REMOTE,
    name: str = COOKIECUTTER_REMOTE_NAME,
    url: str = COOKIECUTTER_REMOTE_URL,
    path: str = COOKIECUTTER_REMOTE_DEFAULT_EXPECT_PATH,
    render_relative_root_in_output: Path = Path("{{ cookiecutter.name }}"),
    render_relative_root_in_template: Path = Path("{{ cookiecutter.name }}"),
    expect_add_mode: AddMode = AddMode.LOCAL,
    num_template_sources: int = 1,
    template_source_index: int = 0,
):
    assert_applied_templates_config_is_correct(
        at_config_path,
        expect_applied_template_root,
        expect_data=expect_data,
        version=version,
        template_source_type=template_source_type,
        name=name,
        expect_add_mode=expect_add_mode,
    )
    assert_template_sources_config_is_correct(
        ts_config_path,
        version=version,
        target_version=target_version,
        name=name,
        url=url,
        path=path,
        render_relative_root_in_output=render_relative_root_in_output,
        render_relative_root_in_template=render_relative_root_in_template,
        num_template_sources=num_template_sources,
        template_source_index=template_source_index,
    )


def assert_project_config_is_correct(
    path: Path = GENERATED_REPO_DIR / "flexlate-project.json",
    user: bool = False,
    add_mode: AddMode = AddMode.LOCAL,
    project_folder_name: str = "project",
    project_containing_folder: Path = GENERATED_FILES_DIR,
):
    expect_project_path = project_containing_folder / project_folder_name
    project_config = FlexlateProjectConfig.load(path)
    assert len(project_config.projects) == 1
    project = project_config.projects[0]
    if user:
        assert project.path == project.path.absolute()
        assert project.path == expect_project_path
    else:
        assert project.path != project.path.absolute()
        assert (path.parent / project.path).absolute() == expect_project_path
    assert project.default_add_mode == add_mode


def _get_default_data(template_source_type: TemplateSourceType) -> TemplateData:
    if template_source_type == TemplateSourceType.COOKIECUTTER_REMOTE:
        return dict(name="abc", key="value")
    elif template_source_type == TemplateSourceType.COPIER_REMOTE:
        return dict(question1="answer1", question2=2.7)
    elif template_source_type == TemplateSourceType.COOKIECUTTER_LOCAL:
        return dict(a="b", c="")
    elif template_source_type == TemplateSourceType.COPIER_LOCAL:
        return dict(q1="a1", q2=1, q3=None)
    else:
        raise ValueError(f"unexpected template source type {template_source_type}")


def assert_root_template_source_output_is_correct(
    template_source: TemplateSourceFixture,
    after_version_update: bool = False,
    after_data_update: bool = False,
    target_version: Optional[str] = None,
    num_template_sources: int = 1,
    template_source_index: int = 0,
):
    version = (
        template_source.version_2 if after_version_update else template_source.version_1
    )
    input_data = (
        template_source.update_input_data
        if after_data_update
        else template_source.input_data
    )
    at_config_path = (
        GENERATED_REPO_DIR
        / template_source.evaluated_render_relative_root_in_output_creator(input_data)
        / "flexlate.json"
    )
    assert_project_files_are_correct(
        expect_data=input_data,
        version=version,
        template_source_type=template_source.type,
    )
    assert_config_is_correct(
        at_config_path=at_config_path,
        expect_applied_template_root=template_source.expect_local_applied_template_path,
        expect_data=input_data,
        version=version,
        target_version=target_version,
        template_source_type=template_source.type,
        name=template_source.name,
        url=template_source.url,
        path=template_source.path,
        render_relative_root_in_output=template_source.render_relative_root_in_output,
        render_relative_root_in_template=template_source.render_relative_root_in_template,
        num_template_sources=num_template_sources,
        template_source_index=template_source_index,
    )
