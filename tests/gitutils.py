from pathlib import Path
from typing import Union

from git import Repo

from tests.config import GENERATED_REPO_DIR, GENERATED_FILES_DIR


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


def rename_branch(repo: Repo, branch_name: str, new_branch_name: str):
    repo.git.branch("-m", branch_name, new_branch_name)


def checkout_new_branch(repo: Repo, branch_name: str):
    repo.git.checkout("-b", branch_name)


def checkout_existing_branch(repo: Repo, branch_name: str):
    repo.git.checkout(branch_name)


def add_remote(repo: Repo, path: Union[str, Path], remote_name: str = "origin"):
    if isinstance(path, Path):
        remote_path = str(path.resolve())
    else:
        remote_path = path
    repo.git.remote("add", remote_name, remote_path)


def add_local_remote(
    repo: Repo, remote_path: Path = GENERATED_FILES_DIR / "remote"
) -> Repo:
    if not remote_path.exists():
        remote_path.mkdir()
    remote_repo = Repo.init(remote_path)
    add_remote(repo, remote_path)
    return remote_repo


def accept_theirs_in_merge_conflict(repo: Repo):
    repo.git.checkout("--theirs", ".")


def reset_n_commits_without_checkout(
    repo: Repo, branch_name: str, n_commits: int = 1, ignore_merges: bool = True
):
    if not ignore_merges:
        reset_to = f"HEAD~{n_commits}"
    else:
        reset_to = _get_last_non_merge_commit_parent_on_branch(repo, branch_name)
    repo.git.branch("--force", branch_name, reset_to)


def _get_last_non_merge_commit_parent_on_branch(repo: Repo, branch_name: str) -> str:
    return repo.git.rev_list("--no-merges", "-n", "1", f"{branch_name}~1")


def _get_main_message_from_commit_message(message: str) -> str:
    return message.split("\n")[0]
