# Integration tests
import os

from flexlate.main import Flexlate
from tests.config import GENERATED_FILES_DIR, COOKIECUTTER_REMOTE_URL
from tests.dirutils import change_directory_to
from tests.fixtures.git import *


def test_init_project_and_add_source_and_template(repo_with_placeholder_committed: Repo):
    repo = repo_with_placeholder_committed
    fxt = Flexlate()
    with change_directory_to(GENERATED_FILES_DIR):
        fxt.init_project()
        fxt.add_template_source(COOKIECUTTER_REMOTE_URL)
        fxt.apply_template_and_add("cookiecutter-simple-example", no_input=True)
    out_path = GENERATED_FILES_DIR / "abc" / "abc.txt"
    assert out_path.exists()
    content = out_path.read_text()
    assert content == "some new header\nvalue"
