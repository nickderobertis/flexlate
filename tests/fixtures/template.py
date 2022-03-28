import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import List, TypedDict, Union

import pytest

from flexlate.finder.specific.cookiecutter import CookiecutterFinder
from flexlate.finder.specific.copier import CopierFinder
from flexlate.path_ops import change_directory_to
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template_path import get_local_repo_path_and_name_cloning_if_repo_url
from tests.config import (
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_TWO_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_VERSION_2,
    COOKIECUTTER_REMOTE_VERSION_1,
    COPIER_ONE_DIR,
    COPIER_REMOTE_VERSION_2,
    COPIER_REMOTE_VERSION_1,
    COOKIECUTTER_ONE_VERSION,
    COOKIECUTTER_ONE_MODIFIED_VERSION,
    COPIER_ONE_VERSION,
    COPIER_ONE_MODIFIED_VERSION,
    COPIER_OUTPUT_SUBDIR_DIR,
    GENERATED_REPO_DIR,
    COPIER_FROM_COOKIECUTTER_ONE_DIR,
    COPIER_FROM_COOKIECUTTER_ONE_VERSION,
)


class CookiecutterRemoteTemplateData(TypedDict):
    name: str
    key: str


def get_header_for_cookiecutter_remote_template(version: str) -> str:
    if version == COOKIECUTTER_REMOTE_VERSION_2:
        return "some new header\n"
    elif version == COOKIECUTTER_REMOTE_VERSION_1:
        return ""
    else:
        raise ValueError(f"unknown cookiecutter remote version {version}")


def get_footer_for_copier_remote_template(version: str) -> str:
    if version == COPIER_REMOTE_VERSION_2:
        return "\nsome new footer"
    elif version == COPIER_REMOTE_VERSION_1:
        return ""
    else:
        raise ValueError(f"unknown copier remote version {version}")


def get_footer_for_cookiecutter_local_template(version: str) -> str:
    if version == COOKIECUTTER_ONE_MODIFIED_VERSION:
        return " and extra"
    elif version == COOKIECUTTER_ONE_VERSION:
        return ""
    elif version == COPIER_FROM_COOKIECUTTER_ONE_VERSION:
        return ""
    else:
        raise ValueError(f"unknown cookiecutter local version {version}")


def get_footer_for_copier_local_template(version: str) -> str:
    if version == COPIER_ONE_MODIFIED_VERSION:
        return " and some footer"
    elif version == COPIER_ONE_VERSION:
        return ""
    else:
        raise ValueError(f"unknown copier local version {version}")


@pytest.fixture
def cookiecutter_one_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    yield finder.find(str(COOKIECUTTER_ONE_DIR), COOKIECUTTER_ONE_DIR)


@pytest.fixture
def cookiecutter_one_template_in_repo() -> CookiecutterTemplate:
    # NOTE: Must be used in conjunction with an in_repo templated repo because
    # these changes only affect the template and not the generated repo
    new_folder = GENERATED_REPO_DIR / "templates"
    new_folder.mkdir(parents=True)
    new_path = new_folder / COOKIECUTTER_ONE_DIR.name
    shutil.copytree(COOKIECUTTER_ONE_DIR, new_path)
    finder = CookiecutterFinder()
    with change_directory_to(GENERATED_REPO_DIR):
        relative_path = new_path.relative_to(GENERATED_REPO_DIR)
        template = finder.find(str(relative_path), relative_path)
    yield template


@pytest.fixture
def copier_one_template() -> CookiecutterTemplate:
    finder = CopierFinder()
    yield finder.find(str(COPIER_ONE_DIR), COPIER_ONE_DIR)


@pytest.fixture
def copier_output_subdir_template() -> CookiecutterTemplate:
    finder = CopierFinder()
    yield finder.find(str(COPIER_OUTPUT_SUBDIR_DIR), COPIER_OUTPUT_SUBDIR_DIR)


@pytest.fixture
def cookiecutter_two_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    yield finder.find(str(COOKIECUTTER_TWO_DIR), COOKIECUTTER_TWO_DIR)


@pytest.fixture()
def cookiecutter_remote_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        local_path, name = get_local_repo_path_and_name_cloning_if_repo_url(
            COOKIECUTTER_REMOTE_URL, dst_folder=temp_path
        )
        template = finder.find(COOKIECUTTER_REMOTE_URL, local_path, name=name)
        # This would normally happen when loading template from source in config
        template.template_source_path = COOKIECUTTER_REMOTE_URL
        yield template


@pytest.fixture()
def cookiecutter_remote_version_one_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        local_path, name = get_local_repo_path_and_name_cloning_if_repo_url(
            COOKIECUTTER_REMOTE_URL, COOKIECUTTER_REMOTE_VERSION_1, dst_folder=temp_path
        )
        template = finder.find(
            COOKIECUTTER_REMOTE_URL,
            local_path,
            name=name,
            version=COOKIECUTTER_REMOTE_VERSION_1,
        )
        # This would normally happen when loading template from source in config
        template.template_source_path = COOKIECUTTER_REMOTE_URL
        yield template


@pytest.fixture
def cookiecutter_local_templates(
    cookiecutter_one_template: CookiecutterTemplate,
    cookiecutter_two_template: CookiecutterTemplate,
) -> List[CookiecutterTemplate]:
    yield [cookiecutter_one_template, cookiecutter_two_template]


def modify_cookiecutter_one(root: Union[str, Path]):
    text_path = Path(root) / "{{ cookiecutter.a }}" / "text.txt"
    text_path.write_text("{{ cookiecutter.a }}{{ cookiecutter.c }} and extra")


def modify_copier_one(root: Union[str, Path]):
    text_path = Path(root) / "{{ q1 }}.txt.jinja"
    text_path.write_text("{{ q2 }} and some footer")


def modify_cookiecutter_one_to_be_copier(root: Union[str, Path]):
    shutil.rmtree(root)
    shutil.copytree(COPIER_FROM_COOKIECUTTER_ONE_DIR, root)


@pytest.fixture
def cookiecutter_one_modified_template(
    cookiecutter_one_template: CookiecutterTemplate,
) -> CookiecutterTemplate:
    template = deepcopy(cookiecutter_one_template)
    with tempfile.TemporaryDirectory() as directory:
        out_path = Path(directory)
        shutil.copytree(template.path, out_path, dirs_exist_ok=True)
        template.path = out_path
        modify_cookiecutter_one(out_path)
        # Update version
        template.version = template.folder_hash
        yield template
