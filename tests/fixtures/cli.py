from dataclasses import dataclass
from enum import Enum
from typing import List, Final

import pytest

from flexlate.main import Flexlate
from tests.integration.cli_stub import CLIStubFlexlate


class FlexlateType(str, Enum):
    APP = "app"
    CLI = "cli"


@dataclass
class FlexlateFixture:
    flexlate: Flexlate
    type: FlexlateType


# NOTE: If any integration tests are failing, temporarily comment the CLIStubFlexlate
#  fixture while debugging, as the CLI tests are the same but much harder to debug
flexlate_fixtures: Final[List[FlexlateFixture]] = [
    FlexlateFixture(flexlate=Flexlate(), type=FlexlateType.APP),
    FlexlateFixture(flexlate=CLIStubFlexlate(), type=FlexlateType.CLI),
]


@pytest.fixture(scope="module", params=flexlate_fixtures)
def flexlates(request) -> FlexlateFixture:
    return request.param
