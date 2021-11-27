from tests.config import GENERATED_FILES_DIR

COOKIECUTTER_ONE_GENERATED_TEXT_PATH = GENERATED_FILES_DIR / "b" / "text.txt"
COOKIECUTTER_TWO_GENERATED_TEXT_PATH = GENERATED_FILES_DIR / "b" / "text2.txt"


def _generated_text_content(folder: str, file: str) -> str:
    path = GENERATED_FILES_DIR / folder / file
    assert path.exists()
    return path.read_text()


def cookiecutter_one_generated_text_content(
    folder: str = "b", file: str = "text.txt"
) -> str:
    return _generated_text_content(folder, file)


def cookiecutter_two_generated_text_content(
    folder: str = "b", file: str = "text2.txt"
) -> str:
    return _generated_text_content(folder, file)