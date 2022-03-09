from dataclasses import dataclass
from typing import Callable, List, Final

from flexlate.main import Flexlate
from tests.config import COOKIECUTTER_REMOTE_NAME, COPIER_ONE_DIR, COPIER_ONE_NAME
from tests.integration.fixtures.template_source import COOKIECUTTER_REMOTE_FIXTURE


@dataclass
class UndoableOperation:
    operation: Callable[[Flexlate, bool], None]
    num_transactions: int = 1

    @property
    def name(self) -> str:
        return self.operation.__name__


def add_template_source(fxt: Flexlate, is_cli: bool):
    fxt.add_template_source(str(COPIER_ONE_DIR))


def apply_template_and_add(fxt: Flexlate, is_cli: bool):
    fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)


def remove_template_source(fxt: Flexlate, is_cli: bool):
    # Must add the template source so it can be removed. It will be two undo operations
    fxt.add_template_source(str(COPIER_ONE_DIR))
    fxt.remove_template_source(COPIER_ONE_NAME)


def remove_applied_template_and_output(fxt: Flexlate, is_cli: bool):
    # Must add the applied template output so it can be removed. It will be two undo operations
    fxt.apply_template_and_add(COOKIECUTTER_REMOTE_NAME, no_input=True)
    fxt.remove_applied_template_and_output(COOKIECUTTER_REMOTE_NAME)


def update(fxt: Flexlate, is_cli: bool):
    no_input = not is_cli
    fxt.update(data=[COOKIECUTTER_REMOTE_FIXTURE.update_input_data], no_input=no_input)


UNDOABLE_OPERATIONS: Final[List[UndoableOperation]] = [
    UndoableOperation(add_template_source),
    UndoableOperation(apply_template_and_add),
    UndoableOperation(remove_template_source, num_transactions=2),
    UndoableOperation(remove_applied_template_and_output, num_transactions=2),
    UndoableOperation(update),
]
