from functools import partial

from tests.integration.cli_stub import ExceptionHandling
from tests.integration.cli_stub import fxt as _fxt

# Ignore exceptions so that we can test error codes instead
fxt = partial(_fxt, exception_handling=ExceptionHandling.IGNORE)
