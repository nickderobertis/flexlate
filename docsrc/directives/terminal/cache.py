from hashlib import md5
from pathlib import Path
from typing import Sequence, List, Optional

from pydantic import BaseModel

from .options import RunTerminalOptions
from .command import Command


SOURCE_DIR = Path(__file__).parent.parent.parent / "source"
CACHE_DIR = SOURCE_DIR / "cache"
TERMINAL_CACHE_DIR = CACHE_DIR / "terminal"

TERMINAL_CACHE_DIR.mkdir(exist_ok=True, parents=True)


class CacheInputs(BaseModel):
    content: Sequence[str]
    options: RunTerminalOptions

    def __str__(self) -> str:
        return "\n".join([*self.content, self._options_str])

    @property
    def _options_str(self) -> str:
        return str(self.options)

    @property
    def cache_key(self) -> str:
        return md5(str(self).encode()).hexdigest()

    @property
    def file_name(self) -> str:
        return f"{self.cache_key}.txt"


class CacheOutput(BaseModel):
    content: List[str]
    input: CacheInputs

    @property
    def file_name(self) -> str:
        return self.input.file_name


class TerminalCache:
    def __init__(self, cache_dir: Path = TERMINAL_CACHE_DIR):
        self.cache_dir = cache_dir

    def get(
        self, content: Sequence[str], options: RunTerminalOptions
    ) -> Optional[CacheOutput]:
        inputs = CacheInputs(content=content, options=options)
        path = self.cache_dir / inputs.file_name
        if not path.exists():
            print(f"Cache miss for terminal directive: {inputs}")
            return None

        out_content = path.read_text()
        return CacheOutput(content=out_content.splitlines(), input=inputs)

    def set(
        self,
        directive_content: Sequence[str],
        options: RunTerminalOptions,
        output_content: Sequence[str],
    ) -> CacheOutput:
        inputs = CacheInputs(content=directive_content, options=options)
        output = CacheOutput(content=list(output_content), input=inputs)
        path = self.cache_dir / output.file_name
        path.write_text("\n".join(output.content))
        return output
