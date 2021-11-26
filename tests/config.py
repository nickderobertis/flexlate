from pathlib import Path

TESTS_DIR = Path(__file__).parent
INPUT_FILES_DIR = TESTS_DIR / "input_files"
GENERATED_FILES_DIR = TESTS_DIR / "generated"

TEMPLATES_DIR = INPUT_FILES_DIR / "templates"

COOKIECUTTERS_DIR = TEMPLATES_DIR / "cookiecutters"
COOKIECUTTER_ONE_DIR = COOKIECUTTERS_DIR / "one"
COOKIECUTTER_REMOTE_URL = "https://github.com/nickderobertis/cookiecutter-simple-example"


if not GENERATED_FILES_DIR.exists():
    GENERATED_FILES_DIR.mkdir()