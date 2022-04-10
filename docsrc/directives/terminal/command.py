from pathlib import Path

from pydantic import BaseModel


class Command(BaseModel):
    input: str
    output: str
    cwd: Path
