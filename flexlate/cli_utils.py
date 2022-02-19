from rich.prompt import Confirm

from flexlate.styles import print_styled


def confirm_user(prompt: str) -> bool:
    return Confirm.ask(prompt)


def console_print(message: str, style: str, quiet: bool = False):
    if quiet:
        return
    print_styled(message, style)
