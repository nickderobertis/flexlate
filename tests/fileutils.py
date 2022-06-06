from pathlib import Path
from typing import Optional

from tests import config


def _generated_text_content(
    folder: str, file: str, gen_dir: Optional[Path] = None
) -> str:
    gen_dir = gen_dir or config.GENERATED_FILES_DIR
    path = gen_dir / folder / file
    assert path.exists()
    return path.read_text()


def cookiecutter_one_generated_text_content(
    folder: str = "b", file: str = "text.txt", gen_dir: Optional[Path] = None
) -> str:
    gen_dir = gen_dir or config.GENERATED_FILES_DIR
    return _generated_text_content(folder, file, gen_dir=gen_dir)


def cookiecutter_two_generated_text_content(
    folder: str = "b", file: str = "text2.txt", gen_dir: Optional[Path] = None
) -> str:
    gen_dir = gen_dir or config.GENERATED_FILES_DIR
    return _generated_text_content(folder, file, gen_dir=gen_dir)


def preprend_cookiecutter_one_generated_text(content: str):
    COOKIECUTTER_ONE_GENERATED_TEXT_PATH = config.GENERATED_REPO_DIR / "b" / "text.txt"
    current_content = COOKIECUTTER_ONE_GENERATED_TEXT_PATH.read_text()
    full_content = content + current_content
    COOKIECUTTER_ONE_GENERATED_TEXT_PATH.write_text(full_content)
