from typing import Final

from rich import print

ACTION_REQUIRED_STYLE: Final[str] = "[yellow]:pencil:"
QUESTION_STYLE: Final[str] = ":question:"
ALERT_STYLE: Final[str] = "[red]:x:"


def styled(message: str, style: str) -> str:
    return f"{style}{message}"


def print_styled(message: str, style: str):
    print(styled(message, style))
