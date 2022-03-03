from dataclasses import dataclass
from enum import Enum
from typing import List, Final

import pytest

from flexlate.main import Flexlate
from tests.integration.cli_stub import CLIStubFlexlate, ExceptionHandling


class FlexlateType(str, Enum):
    APP = "app"
    CLI = "cli"


@dataclass
class FlexlateFixture:
    flexlate: Flexlate
    type: FlexlateType


flexlate_app_fixture: Final[FlexlateFixture] = FlexlateFixture(
    flexlate=Flexlate(), type=FlexlateType.APP
)

# NOTE: If any integration tests are failing, temporarily comment the CLIStubFlexlate
#  fixture while debugging, as the CLI tests are the same but much harder to debug
flexlate_fixtures: Final[List[FlexlateFixture]] = [
    flexlate_app_fixture,
    FlexlateFixture(flexlate=CLIStubFlexlate(), type=FlexlateType.CLI),
]

flexlate_ignore_cli_exceptions_fixtures: Final[List[FlexlateFixture]] = [
    flexlate_app_fixture,
    FlexlateFixture(
        flexlate=CLIStubFlexlate(exception_handling=ExceptionHandling.IGNORE),
        type=FlexlateType.CLI,
    ),
]


@pytest.fixture(scope="module", params=flexlate_fixtures)
def flexlates(request) -> FlexlateFixture:
    return request.param


@pytest.fixture(scope="module", params=flexlate_ignore_cli_exceptions_fixtures)
def flexlates_ignore_cli_exceptions(request) -> FlexlateFixture:
    return request.param
