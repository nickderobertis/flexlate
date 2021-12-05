from pathlib import Path

from git import Repo

from tests.config import GENERATED_REPO_DIR


def create_empty_repo(out_dir: Path = GENERATED_REPO_DIR) -> Repo:
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
