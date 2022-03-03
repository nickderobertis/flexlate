import sys
from contextlib import contextmanager
from functools import wraps
from types import TracebackType
from typing import Callable, Type, Tuple

from flexlate.styles import print_styled, ALERT_STYLE


def simple_output_for_exceptions(*exceptions: Type[BaseException]):
    exception_handler = _create_exception_handler(exceptions)

    def _simple_output_for_exceptions(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with _handle_exceptions_with(exception_handler):
                return func(*args, **kwargs)

        return wrapper

    return _simple_output_for_exceptions


ExceptionHandler = Callable[[Type[BaseException], BaseException, TracebackType], None]


@contextmanager
def _handle_exceptions_with(exc_handler: ExceptionHandler):
    "Sets a custom exception handler for the scope of a 'with' block."
    sys.excepthook = exc_handler  #  type: ignore
    yield
    sys.excepthook = sys.__excepthook__  # type: ignore


def _create_exception_handler(
    exceptions: Tuple[Type[BaseException], ...]
) -> ExceptionHandler:
    def handle_specific_exceptions(
        type_: Type[BaseException], value: BaseException, traceback: TracebackType
    ):
        if isinstance(value, exceptions):
            print_styled(f"{type_.__name__}: {value}", ALERT_STYLE)
        else:
            sys.__excepthook__(type_, value, traceback)

    return handle_specific_exceptions
