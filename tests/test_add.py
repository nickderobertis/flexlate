import os
from dataclasses import dataclass
from unittest.mock import patch

import appdirs
from git import Head

from flexlate.add_mode import AddMode
from flexlate.config import FlexlateConfig, FlexlateProjectConfig
from flexlate.constants import DEFAULT_MERGED_BRANCH_NAME, DEFAULT_TEMPLATE_BRANCH_NAME
from flexlate.template.types import TemplateType
from flexlate.transactions.transaction import FlexlateTransaction
from tests.config import GENERATED_FILES_DIR
from tests.fileutils import cookiecutter_one_generated_text_content
from tests.fixtures.git import *
from tests.fixtures.subdir_style import SubdirStyle, subdir_style
from tests.fixtures.template import *
from tests.fixtures.templated_repo import *
from tests.fixtures.add_mode import add_mode
from tests.fixtures.transaction import add_source_transaction, add_output_transaction


def test_add_template_source_to_repo(
    repo_with_placeholder_committed: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
):
    repo = repo_with_placeholder_committed
    adder = Adder()
    adder.add_template_source(
        repo,
        cookiecutter_one_template,
        add_source_transaction,
        out_root=GENERATED_REPO_DIR,
        target_version="some version",
    )
    config_path = GENERATED_REPO_DIR / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 0
    assert len(config.template_sources) == 1
    source = config.template_sources[0]
    assert source.name == cookiecutter_one_template.name
    assert source.path == str(cookiecutter_one_template.path)
    assert source.version == cookiecutter_one_template.version
    assert source.type == TemplateType.COOKIECUTTER
    assert source.target_version == "some version"
    assert source.render_relative_root_in_output == Path("{{ cookiecutter.a }}")
    assert source.render_relative_root_in_template == Path("{{ cookiecutter.a }}")


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_add_local_cookiecutter_applied_template_to_repo(
    add_mode: AddMode,
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    template = cookiecutter_one_template
    adder = Adder()
    adder.apply_template_and_add(
        repo,
        template,
        add_output_transaction,
        out_root=GENERATED_REPO_DIR,
        add_mode=add_mode,
        no_input=True,
    )

    if add_mode == AddMode.USER:
        config_dir = GENERATED_FILES_DIR
        template_root = GENERATED_REPO_DIR.absolute()
    elif add_mode == AddMode.PROJECT:
        config_dir = GENERATED_REPO_DIR
        template_root = Path(".")
    elif add_mode == AddMode.LOCAL:
        # Template has output in a subdir, so with
        # local mode config will also be in the subdir
        config_dir = GENERATED_REPO_DIR / "b"
        template_root = Path("..")
    else:
        raise ValueError(f"unsupported add mode {add_mode}")

    config_path = config_dir / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"a": "b", "c": ""}
    assert at.root == template_root
    assert at.add_mode == add_mode


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_add_local_copier_output_subdir_applied_template_to_repo(
    add_mode: AddMode,
    repo_with_copier_output_subdir_template_source: Repo,
    copier_output_subdir_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
):
    repo = repo_with_copier_output_subdir_template_source
    template = copier_output_subdir_template
    adder = Adder()
    adder.apply_template_and_add(
        repo,
        template,
        add_output_transaction,
        out_root=GENERATED_REPO_DIR,
        add_mode=add_mode,
        no_input=True,
    )

    if add_mode == AddMode.USER:
        config_dir = GENERATED_FILES_DIR
        template_root = GENERATED_REPO_DIR.absolute()
    elif add_mode == AddMode.PROJECT:
        config_dir = GENERATED_REPO_DIR
        template_root = Path(".")
    elif add_mode == AddMode.LOCAL:
        # Even though template has output in a subdir, with copier
        # it all still renders at root in output
        config_dir = GENERATED_REPO_DIR
        template_root = Path(".")
    else:
        raise ValueError(f"unsupported add mode {add_mode}")

    config_path = config_dir / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"qone": "aone", "qtwo": "atwo"}
    assert at.root == template_root
    assert at.add_mode == add_mode


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_add_remote_cookiecutter_applied_template_to_repo(
    add_mode: AddMode,
    repo_with_remote_cookiecutter_template_source: Repo,
    cookiecutter_remote_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
):
    repo = repo_with_remote_cookiecutter_template_source
    template = cookiecutter_remote_template
    adder = Adder()
    adder.apply_template_and_add(
        repo,
        template,
        add_output_transaction,
        out_root=GENERATED_REPO_DIR,
        add_mode=add_mode,
        no_input=True,
    )

    if add_mode == AddMode.USER:
        config_dir = GENERATED_FILES_DIR
        template_root = GENERATED_REPO_DIR.absolute()
    elif add_mode == AddMode.PROJECT:
        config_dir = GENERATED_REPO_DIR
        template_root = Path(".")
    elif add_mode == AddMode.LOCAL:
        config_dir = GENERATED_REPO_DIR / "abc"
        template_root = Path("..")
    else:
        raise ValueError(f"unsupported add mode {add_mode}")

    config_path = config_dir / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"name": "abc", "key": "value"}
    assert at.root == template_root
    assert at.add_mode == add_mode


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_add_applied_template_to_subdir(
    add_mode: AddMode,
    subdir_style: SubdirStyle,
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    template = cookiecutter_one_template
    subdir = GENERATED_REPO_DIR / "subdir1" / "subdir2"
    subdir.mkdir(parents=True)
    adder = Adder()
    if subdir_style == SubdirStyle.CD:
        with change_directory_to(subdir):
            adder.apply_template_and_add(
                repo, template, add_output_transaction, add_mode=add_mode, no_input=True
            )
    elif subdir_style == SubdirStyle.PROVIDE_RELATIVE:
        with change_directory_to(GENERATED_REPO_DIR):
            adder.apply_template_and_add(
                repo,
                template,
                add_output_transaction,
                out_root=subdir.relative_to(os.getcwd()),
                add_mode=add_mode,
                no_input=True,
            )
    elif subdir_style == SubdirStyle.PROVIDE_ABSOLUTE:
        adder.apply_template_and_add(
            repo,
            template,
            add_output_transaction,
            out_root=subdir.absolute(),
            add_mode=add_mode,
            no_input=True,
        )

    if add_mode == AddMode.LOCAL:
        config_dir = subdir / "b"
        template_root = Path("..")
    elif add_mode == AddMode.PROJECT:
        config_dir = GENERATED_REPO_DIR
        template_root = subdir.relative_to(GENERATED_REPO_DIR)
    elif add_mode == AddMode.USER:
        config_dir = GENERATED_FILES_DIR
        template_root = subdir.absolute()
    else:
        raise ValueError(f"unsupported add mode {add_mode}")

    config_path = config_dir / "flexlate.json"
    config = FlexlateConfig.load(config_path)
    assert len(config.applied_templates) == 1
    at = config.applied_templates[0]
    assert at.name == template.name
    assert at.version == template.version
    assert at.data == {"a": "b", "c": ""}
    assert at.root == template_root
    assert at.add_mode == add_mode

    output_file_path = subdir / "b" / "text.txt"
    assert output_file_path.read_text() == "b"


@patch.object(appdirs, "user_config_dir", lambda name: GENERATED_FILES_DIR)
def test_add_multiple_applied_templates_for_one_source(
    add_mode: AddMode,
    repo_with_cookiecutter_one_template_source: Repo,
    cookiecutter_one_template: CookiecutterTemplate,
    add_output_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source
    template = cookiecutter_one_template
    subdir = GENERATED_REPO_DIR / "subdir1" / "subdir2"
    subdir.mkdir(parents=True)
    adder = Adder()
    with change_directory_to(GENERATED_REPO_DIR):
        adder.apply_template_and_add(
            repo, template, add_output_transaction, add_mode=add_mode, no_input=True
        )
    with change_directory_to(subdir):
        adder.apply_template_and_add(
            repo, template, add_output_transaction, add_mode=add_mode, no_input=True
        )

    @dataclass
    class OutputOptions:
        config_dir: Path
        template_root: Path
        render_root: Path
        expect_num_applied_templates: int = 1
        applied_template_index: int = 0

    output_options: List[OutputOptions] = []
    if add_mode == AddMode.LOCAL:
        output_options.extend(
            [
                OutputOptions(GENERATED_REPO_DIR / "b", Path(".."), GENERATED_REPO_DIR),
                OutputOptions(subdir / "b", Path(".."), subdir),
            ]
        )
    elif add_mode == AddMode.PROJECT:
        output_options.extend(
            [
                OutputOptions(
                    GENERATED_REPO_DIR,
                    Path("."),
                    GENERATED_REPO_DIR,
                    expect_num_applied_templates=2,
                ),
                OutputOptions(
                    GENERATED_REPO_DIR,
                    subdir.relative_to(GENERATED_REPO_DIR),
                    subdir,
                    expect_num_applied_templates=2,
                    applied_template_index=1,
                ),
            ]
        )
    elif add_mode == AddMode.USER:
        output_options.extend(
            [
                OutputOptions(
                    GENERATED_FILES_DIR,
                    GENERATED_REPO_DIR.absolute(),
                    GENERATED_REPO_DIR,
                    expect_num_applied_templates=2,
                ),
                OutputOptions(
                    GENERATED_FILES_DIR,
                    subdir.absolute(),
                    subdir,
                    expect_num_applied_templates=2,
                    applied_template_index=1,
                ),
            ]
        )
    else:
        raise ValueError(f"unsupported add mode {add_mode}")

    for output_option in output_options:
        config_dir = output_option.config_dir
        template_root = output_option.template_root
        render_root = output_option.render_root
        expect_num_applied_templates = output_option.expect_num_applied_templates
        applied_template_index = output_option.applied_template_index
        config_path = config_dir / "flexlate.json"
        config = FlexlateConfig.load(config_path)
        assert len(config.applied_templates) == expect_num_applied_templates
        at = config.applied_templates[applied_template_index]
        assert at.name == template.name
        assert at.version == template.version
        assert at.data == {"a": "b", "c": ""}
        assert at.root == template_root
        assert at.add_mode == add_mode

        output_file_path = render_root / "b" / "text.txt"
        assert output_file_path.read_text() == "b"


def test_add_source_to_project_with_existing_outputs(
    repo_with_cookiecutter_one_template_source_and_output: Repo,
    cookiecutter_two_template: CookiecutterTemplate,
    add_source_transaction: FlexlateTransaction,
):
    repo = repo_with_cookiecutter_one_template_source_and_output
    adder = Adder()
    adder.add_template_source(
        repo,
        cookiecutter_two_template,
        add_source_transaction,
        out_root=GENERATED_REPO_DIR,
        target_version="some version",
    )
    assert cookiecutter_one_generated_text_content(gen_dir=GENERATED_REPO_DIR) == "b"
    source_config_path = GENERATED_REPO_DIR / "flexlate.json"
    source_config = FlexlateConfig.load(source_config_path)
    assert len(source_config.applied_templates) == 0
    assert len(source_config.template_sources) == 2
    source = source_config.template_sources[1]
    assert source.name == cookiecutter_two_template.name
    assert source.path == str(cookiecutter_two_template.path)
    assert source.version == cookiecutter_two_template.version
    assert source.type == TemplateType.COOKIECUTTER
    assert source.target_version == "some version"
    assert source.render_relative_root_in_output == Path("{{ cookiecutter.a }}")
    assert source.render_relative_root_in_template == Path("{{ cookiecutter.a }}")
    at_config_path = GENERATED_REPO_DIR / "b" / "flexlate.json"
    at_config = FlexlateConfig.load(at_config_path)
    assert len(at_config.applied_templates) == 1


# TODO: test for adding to existing


def test_add_project_config_with_git(repo_with_placeholder_committed: Repo):
    repo = repo_with_placeholder_committed
    adder = Adder()
    adder.init_project_and_add_to_branches(repo)

    for branch_name in [
        "master",
        DEFAULT_MERGED_BRANCH_NAME,
        DEFAULT_TEMPLATE_BRANCH_NAME,
    ]:
        branch: Head = repo.branches[branch_name]  # type: ignore
        branch.checkout()
        config = FlexlateProjectConfig.load(
            GENERATED_REPO_DIR / "flexlate-project.json"
        )
        assert len(config.projects) == 1
        project = config.projects[0]
        assert project.path == Path(".")


def test_init_project_from_template_source_path():
    adder = Adder()
    adder.init_project_from_template_source_path(COOKIECUTTER_REMOTE_URL)
