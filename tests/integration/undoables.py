from typing import Callable, List, Final

from flexlate.main import Flexlate
from tests.config import COOKIECUTTER_REMOTE_NAME, COPIER_ONE_DIR
from tests.fixtures.template_source import COOKIECUTTER_REMOTE_FIXTURE


def add_template_source(fxt: Flexlate):
    fxt.add_template_source(str(COPIER_ONE_DIR))


def apply_template_and_add(fxt: Flexlate):
    fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)


def remove_template_source(fxt: Flexlate):
    fxt.remove_template_source(COOKIECUTTER_REMOTE_NAME)


def remove_applied_template_and_output(fxt: Flexlate):
    fxt.remove_applied_template_and_output(COOKIECUTTER_REMOTE_NAME)


def update(fxt: Flexlate):
    fxt.update(data=[COOKIECUTTER_REMOTE_FIXTURE.update_input_data], no_input=True)


UNDOABLE_OPERATIONS: Final[List[Callable[[Flexlate], None]]] = [
    add_template_source,
    apply_template_and_add,
    remove_template_source,
    remove_applied_template_and_output,
    update,
]
