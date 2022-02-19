from typing import Final

from rich.console import Console

console: Final[Console] = Console()


ACTION_REQUIRED_STYLE: Final[str] = "[yellow]:pencil:"
QUESTION_STYLE: Final[str] = ":question:"
ALERT_STYLE: Final[str] = "[red]:x:"
INFO_STYLE: Final[str] = ""
SUCCESS_STYLE: Final[str] = "[green]:heavy_check_mark:"


def styled(message: str, style: str) -> str:
    return f"{style} {message}"


def print_styled(message: str, style: str):
    console.print(styled(message, style))
