from typing import List, Optional
from typing_extensions import TypedDict

RunTerminalOptions = TypedDict(
    "RunTerminalOptions",
    {
        "setup": str,
        "input": List[Optional[str]],
        "allow-exceptions": Optional[bool],
    },
    total=False,
)
