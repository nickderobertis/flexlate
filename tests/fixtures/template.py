import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import List, TypedDict, Union

import pytest

from flexlate.finder.specific.cookiecutter import CookiecutterFinder
from flexlate.finder.specific.copier import CopierFinder
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
def copier_one_template() -> CookiecutterTemplate:
    finder = CopierFinder()
    yield finder.find(str(COPIER_ONE_DIR), COPIER_ONE_DIR)


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
        yield finder.find(COOKIECUTTER_REMOTE_URL, local_path, name=name)


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
