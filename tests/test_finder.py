import tempfile
from pathlib import Path

import pytest

from flexlate.finder.multi import MultiFinder
from flexlate.finder.specific.cookiecutter import CookiecutterFinder
from flexlate.finder.specific.copier import CopierFinder
from flexlate.path_ops import change_directory_to
from flexlate.template.base import Template
from flexlate.template.cookiecutter import CookiecutterTemplate
from flexlate.template_path import get_local_repo_path_and_name_cloning_if_repo_url
from tests.config import (
    COOKIECUTTER_ONE_DIR,
    COOKIECUTTER_REMOTE_URL,
    COOKIECUTTER_REMOTE_VERSION_1,
    COOKIECUTTER_REMOTE_VERSION_2,
    COOKIECUTTER_ONE_VERSION,
    COPIER_ONE_DIR,
    COPIER_ONE_VERSION,
    COPIER_REMOTE_VERSION_1,
    COPIER_REMOTE_VERSION_2,
    COPIER_REMOTE_URL,
    COPIER_REMOTE_NAME,
    COOKIECUTTER_REMOTE_NAME,
    COPIER_ONE_NAME,
    COOKIECUTTER_ONE_NAME,
    GENERATED_FILES_DIR,
    COPIER_OUTPUT_SUBDIR_VERSION,
    COPIER_OUTPUT_SUBDIR_NAME,
    COPIER_OUTPUT_SUBDIR_DIR,
)


def test_get_cookiecutter_config():
    finder = CookiecutterFinder()
    config = finder.get_config(COOKIECUTTER_ONE_DIR)
    assert config.defaults == {"a": "b", "c": ""}


def test_get_copier_config():
    finder = CopierFinder()
    config = finder.get_config(COPIER_ONE_DIR)
    assert config.defaults == {"q1": "a1", "q2": 1, "q3": None}


def test_get_cookiecutter_local_template():
    finder = CookiecutterFinder()
    template = finder.find(str(COOKIECUTTER_ONE_DIR), COOKIECUTTER_ONE_DIR)
    _assert_template_matches_cookiecutter_one(template)


def _assert_template_matches_cookiecutter_one(
    template: Template, expect_path: Path = COOKIECUTTER_ONE_DIR
):
    assert template.path == expect_path
    assert template.name == COOKIECUTTER_ONE_NAME
    assert template.git_url is None
    assert template.version == COOKIECUTTER_ONE_VERSION
    assert template.config.defaults == {"a": "b", "c": ""}
    assert template.render_relative_root_in_output == Path("{{ cookiecutter.a }}")
    assert template.render_relative_root_in_template == Path("{{ cookiecutter.a }}")


def test_get_copier_local_template():
    finder = CopierFinder()
    template = finder.find(str(COPIER_ONE_DIR), COPIER_ONE_DIR)
    assert template.path == COPIER_ONE_DIR
    assert template.name == COPIER_ONE_NAME
    assert template.git_url is None
    assert template.version == COPIER_ONE_VERSION
    assert template.config.defaults == {"q1": "a1", "q2": 1, "q3": None}
    assert template.render_relative_root_in_output == Path(".")
    assert template.render_relative_root_in_template == Path(".")


def test_get_copier_local_output_subdir_template():
    finder = CopierFinder()
    template = finder.find(str(COPIER_OUTPUT_SUBDIR_DIR), COPIER_OUTPUT_SUBDIR_DIR)
    assert template.path == COPIER_OUTPUT_SUBDIR_DIR
    assert template.name == COPIER_OUTPUT_SUBDIR_NAME
    assert template.git_url is None
    assert template.version == COPIER_OUTPUT_SUBDIR_VERSION
    assert template.config.defaults == {"qone": "aone", "qtwo": "atwo"}
    assert template.render_relative_root_in_output == Path(".")
    assert template.render_relative_root_in_template == Path("output")


@pytest.mark.parametrize(
    "version, expect_contents",
    [
        (COOKIECUTTER_REMOTE_VERSION_1, "{{ cookiecutter.key }}"),
        (COOKIECUTTER_REMOTE_VERSION_2, "some new header\n{{ cookiecutter.key }}"),
    ],
)
def test_get_cookiecutter_remote_template(version: str, expect_contents: str):
    finder = CookiecutterFinder()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        local_path, name = get_local_repo_path_and_name_cloning_if_repo_url(
            COOKIECUTTER_REMOTE_URL, version, dst_folder=temp_path
        )
        template = finder.find(
            COOKIECUTTER_REMOTE_URL, local_path, version=version, name=name
        )
        assert template.path == temp_path / COOKIECUTTER_REMOTE_NAME / version
        assert template.git_url == COOKIECUTTER_REMOTE_URL
        assert template.name == COOKIECUTTER_REMOTE_NAME
        assert template.version == version
        assert template.config.defaults == {"name": "abc", "key": "value"}
        assert template.render_relative_root_in_output == Path(
            "{{ cookiecutter.name }}"
        )
        assert template.render_relative_root_in_template == Path(
            "{{ cookiecutter.name }}"
        )
        template_file = (
            template.path / "{{ cookiecutter.name }}" / "{{ cookiecutter.name }}.txt"
        )
        assert template_file.read_text() == expect_contents


@pytest.mark.parametrize(
    "version, expect_contents",
    [
        (COPIER_REMOTE_VERSION_1, "{{ question2 }}"),
        (COPIER_REMOTE_VERSION_2, "{{ question2 }}\nsome new footer"),
    ],
)
def test_get_copier_remote_template(version: str, expect_contents: str):
    finder = CopierFinder()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        local_path, name = get_local_repo_path_and_name_cloning_if_repo_url(
            COPIER_REMOTE_URL, version, dst_folder=temp_path
        )
        template = finder.find(
            COPIER_REMOTE_URL, local_path, version=version, name=name
        )
        assert template.path == temp_path / COPIER_REMOTE_NAME / version
        assert template.git_url == COPIER_REMOTE_URL
        assert template.name == COPIER_REMOTE_NAME
        assert template.version == version
        assert template.config.defaults == {"question1": "answer1", "question2": 2.7}
        assert template.render_relative_root_in_output == Path(".")
        assert template.render_relative_root_in_template == Path("output")
        template_file = template.path / "output" / "{{ question1 }}.txt.jinja"
        assert template_file.read_text() == expect_contents


def test_multi_finder_get_cookiecutter_local_template():
    finder = MultiFinder()
    template = finder.find(str(COOKIECUTTER_ONE_DIR))
    _assert_template_matches_cookiecutter_one(template)


def test_multi_finder_get_cookiecutter_local_template_from_current_directory():
    finder = MultiFinder()
    with change_directory_to(COOKIECUTTER_ONE_DIR):
        template = finder.find(str("."))
    _assert_template_matches_cookiecutter_one(template, expect_path=Path("."))


def test_multi_finder_get_copier_local_template():
    finder = MultiFinder()
    template = finder.find(str(COPIER_ONE_DIR))
    assert template.path == COPIER_ONE_DIR
    assert template.git_url is None
    assert template.version == COPIER_ONE_VERSION
    assert template.config.defaults == {"q1": "a1", "q2": 1, "q3": None}
    assert template.render_relative_root_in_output == Path(".")
    assert template.render_relative_root_in_template == Path(".")


@pytest.mark.parametrize(
    "version, expect_contents",
    [
        (COOKIECUTTER_REMOTE_VERSION_1, "{{ cookiecutter.key }}"),
        (COOKIECUTTER_REMOTE_VERSION_2, "some new header\n{{ cookiecutter.key }}"),
    ],
)
def test_multi_finder_get_cookiecutter_remote_template(
    version: str, expect_contents: str
):
    finder = MultiFinder()
    template = finder.find(COOKIECUTTER_REMOTE_URL, version=version)
    assert template.path == GENERATED_FILES_DIR / COOKIECUTTER_REMOTE_NAME / version
    assert template.git_url == COOKIECUTTER_REMOTE_URL
    assert template.version == version
    assert template.config.defaults == {"name": "abc", "key": "value"}
    assert template.render_relative_root_in_output == Path("{{ cookiecutter.name }}")
    assert template.render_relative_root_in_template == Path("{{ cookiecutter.name }}")
    template_file = (
        template.path / "{{ cookiecutter.name }}" / "{{ cookiecutter.name }}.txt"
    )
    assert template_file.read_text() == expect_contents


@pytest.mark.parametrize(
    "version, expect_contents",
    [
        (COPIER_REMOTE_VERSION_1, "{{ question2 }}"),
        (COPIER_REMOTE_VERSION_2, "{{ question2 }}\nsome new footer"),
    ],
)
def test_multi_finder_get_copier_remote_template(version: str, expect_contents: str):
    finder = MultiFinder()
    template = finder.find(COPIER_REMOTE_URL, version=version)
    assert template.path == GENERATED_FILES_DIR / COPIER_REMOTE_NAME / version
    assert template.git_url == COPIER_REMOTE_URL
    assert template.version == version
    assert template.config.defaults == {"question1": "answer1", "question2": 2.7}
    assert template.render_relative_root_in_output == Path(".")
    assert template.render_relative_root_in_template == Path("output")
    template_file = template.path / "output" / "{{ question1 }}.txt.jinja"
    assert template_file.read_text() == expect_contents
