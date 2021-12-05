import shutil
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import List

import pytest

from flexlate.finder.specific.cookiecutter import CookiecutterFinder
from flexlate.template.cookiecutter import CookiecutterTemplate
from tests.config import (
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_TWO_DIR,
    COOKIECUTTER_REMOTE_URL,
)


@pytest.fixture
def cookiecutter_one_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    yield finder.find(COOKIECUTTER_ONE_DIR)


@pytest.fixture
def cookiecutter_two_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    yield finder.find(COOKIECUTTER_TWO_DIR)


@pytest.fixture()
def cookiecutter_remote_template() -> CookiecutterTemplate:
    finder = CookiecutterFinder()
    yield finder.find(COOKIECUTTER_REMOTE_URL)


@pytest.fixture
def cookiecutter_local_templates(
    cookiecutter_one_template: CookiecutterTemplate,
    cookiecutter_two_template: CookiecutterTemplate,
) -> List[CookiecutterTemplate]:
    yield [cookiecutter_one_template, cookiecutter_two_template]


@pytest.fixture
def cookiecutter_one_modified_template(
    cookiecutter_one_template: CookiecutterTemplate,
) -> CookiecutterTemplate:
    template = deepcopy(cookiecutter_one_template)
    with tempfile.TemporaryDirectory() as directory:
        out_path = Path(directory)
        shutil.copytree(template.path, out_path, dirs_exist_ok=True)
        template.path = out_path
        text_path = out_path / "{{ cookiecutter.a }}" / "text.txt"
        text_path.write_text("{{ cookiecutter.c }} and extra")
        # Update version
        template.version = template.folder_hash
        yield template
