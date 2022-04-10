from typing import TypedDict, List, Optional

RunTerminalOptions = TypedDict(
    "RunTerminalOptions",
    {
        "setup": str,
        "input": List[Optional[str]],
        "allow-exceptions": Optional[bool],
    },
    total=False,
)
