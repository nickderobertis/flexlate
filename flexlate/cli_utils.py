from rich.prompt import Confirm


def confirm_user(prompt: str) -> bool:
    return Confirm.ask(prompt)
