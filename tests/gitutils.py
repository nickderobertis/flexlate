from pathlib import Path

from git import Repo

from tests.config import GENERATED_REPO_DIR


def create_empty_repo(out_dir: Path = GENERATED_REPO_DIR) -> Repo:
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
    return Repo.init(out_dir)


def add_dummy_file_to_repo(repo: Repo):
    folder = repo.working_dir
    out_folder = Path(folder) / "some-dir"
    out_folder.mkdir()
    out_path = out_folder / "placeholder.txt"
    out_path.write_text("some text")


def add_dummy_file2_to_repo(repo: Repo):
    folder = repo.working_dir
    out_folder = Path(folder) / "some-dir"
    out_path = out_folder / "placeholder2.txt"
    out_path.write_text("some text2")


def add_gitignore_and_ignored_file_to_repo(repo: Repo):
    folder = repo.working_dir
    out_folder = Path(folder) / "ignored"
    out_folder.mkdir()
    out_path = out_folder / "ignored.txt"
    out_path.write_text("this should be ignored in git")
    gitignore_path = Path(folder) / ".gitignore"
    gitignore_path.write_text("ignored\n")


def assert_main_commit_message_matches(message1: str, message2: str):
    main_1 = _get_main_message_from_commit_message(message1)
    main_2 = _get_main_message_from_commit_message(message2)
    assert main_1 == main_2


def _get_main_message_from_commit_message(message: str) -> str:
    return message.split("\n")[0]
