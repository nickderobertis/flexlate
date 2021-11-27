from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent

TESTS_DIR = Path(__file__).parent
INPUT_FILES_DIR = TESTS_DIR / "input_files"
GENERATED_FILES_DIR = TESTS_DIR / "generated"

TEMPLATES_DIR = INPUT_FILES_DIR / "templates"

COOKIECUTTERS_DIR = TEMPLATES_DIR / "cookiecutters"
COOKIECUTTER_ONE_DIR = COOKIECUTTERS_DIR / "one"
COOKIECUTTER_TWO_DIR = COOKIECUTTERS_DIR / "two"
COOKIECUTTER_REMOTE_URL = "https://github.com/nickderobertis/cookiecutter-simple-example"

CONFIGS_DIR = INPUT_FILES_DIR / "configs"
CONFIG_1_PATH = CONFIGS_DIR / "flexlate.json"
CONFIG_SUBDIR_1 = CONFIG_1_PATH / "subdir1"
CONFIG_SUBDIR_2 = CONFIGS_DIR / "subdir2"


if not GENERATED_FILES_DIR.exists():
    GENERATED_FILES_DIR.mkdir()