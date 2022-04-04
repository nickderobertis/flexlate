import itertools
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import cast, Set, Generator, ContextManager, Optional, Tuple, List, Sequence

from git import Repo, Blob, Tree, GitCommandError, Commit, Git  # type: ignore

from flexlate.exc import (
    GitRepoDirtyException,
    GitRepoHasNoCommitsException,
    CannotFindClonedTemplateException,
)
from flexlate.path_ops import copy_flexlate_configs, change_directory_to


def checkout_template_branch(repo: Repo, branch_name: str, base_branch_name: str):
    try:
        # Get branch if it exists already
        branch = repo.branches[branch_name]  # type: ignore
    except IndexError as e:
        if "No item found with id" in str(e) and branch_name in str(e):
            # Could not find branch, must not exist, create it
            if branch_exists(repo, base_branch_name):
                # Base branch exists, branch off it for feature branch
                target = base_branch_name
            else:
                # Base branch doesn't exist, use the initial commit
                target = repo.git.rev_list("HEAD", max_parents=0)

            branch = repo.create_head(branch_name, target)
        else:
            # Unknown error, raise it
            raise e

    branch.checkout()


def _get_initial_commit_sha(repo: Repo) -> str:
    return repo.git.rev_list("HEAD", max_parents=0)


def _get_initial_commit(repo: Repo) -> Commit:
    return repo.commit(_get_initial_commit_sha(repo))


def stage_and_commit_all(repo: Repo, commit_message: str):
    repo.git.add("-A")
    repo.git.commit("-m", commit_message)


def list_tracked_files(repo: Repo) -> Set[Path]:
    if repo.working_dir is None:
        raise ValueError("repo working dir should not be none")
    return _list_tracked_files(repo.tree(), Path(repo.working_dir))


def _list_tracked_files(tree: Tree, root_path: Path) -> Set[Path]:
    # TODO: Fix multiple iterations over files for git traverse
    #  For now just using a set to keep it working, but should optimize
    files: Set[Path] = set()
    for tree_or_blob in tree.traverse():
        if hasattr(tree_or_blob, "traverse"):
            # Got another tree
            tree = cast(Tree, tree_or_blob)
            files.update(_list_tracked_files(tree, root_path))
        else:
            # Got a blob
            blob = cast(Blob, tree_or_blob)
            files.add(root_path / Path(blob.path))
    return files


def delete_all_tracked_files(repo: Repo):
    if repo.working_dir is None:
        raise ValueError("repo working dir should not be none")
    for path in list_tracked_files(repo):
        os.remove(path)


def restore_initial_commit_files(repo: Repo):
    if repo.working_dir is None:
        raise ValueError("repo working dir must not be None")
    inital_commit = _get_initial_commit(repo)
    initial_commit_files = _list_tracked_files(
        inital_commit.tree, Path(repo.working_dir)
    )
    for file in initial_commit_files:
        if not file.exists():
            _check_out_specific_file_from_commit(repo, inital_commit.hexsha, file)


def _check_out_specific_file_from_commit(repo: Repo, commit_sha: str, file_path: Path):
    relative_path = os.path.relpath(file_path, repo.working_dir)
    repo.git.checkout(commit_sha, relative_path)


def merge_branch_into_current(
    repo: Repo, branch_name: str, allow_conflicts: bool = True
):
    try:
        repo.git.merge(branch_name)
    except GitCommandError as e:
        if allow_conflicts and "fix conflicts and then commit the result" in e.stdout:
            #
            return
        raise e


def get_current_version(repo: Repo) -> str:
    return repo.head.commit.hexsha


def fast_forward_branch_without_checkout(repo: Repo, base_branch: str, ff_branch: str):
    repo.git.fetch(repo.working_dir, f"{ff_branch}:{base_branch}")


def reset_branch_to_commit_without_checkout(
    repo: Repo, branch_name: str, commit_sha: Optional[str] = None
):
    if commit_sha is None:
        # Branch didn't previously exist, delete
        delete_local_branch(repo, branch_name)
        return
    repo.git.branch("--force", branch_name, commit_sha)


def abort_merge(repo: Repo):
    repo.git.merge("--abort")


def get_branch_sha(repo: Repo, branch_name: str) -> Optional[str]:
    try:
        branch = repo.branches[branch_name]  # type: ignore
    except IndexError:
        return None
    return branch.commit.hexsha


def delete_local_branch(repo: Repo, branch_name: str):
    repo.git.branch("-D", branch_name)


@contextmanager  # type: ignore
def temp_repo_that_pushes_to_branch(  # type: ignore
    repo: Repo,
    branch_name: str,
    base_branch_name: str,
    delete_tracked_files: bool = False,
    copy_current_configs: bool = True,
    force_push: bool = False,
    additional_branches: Sequence[str] = tuple(),
    remote: str = "origin",
) -> ContextManager[Repo]:
    if repo.working_dir is None:
        raise ValueError("repo working dir must not be None")
    folder_name = Path(repo.working_dir).name
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / folder_name
        temp_repo = _clone_from_local_repo(
            repo,
            tmp_path,
            branch_name,
            base_branch_name,
            additional_branches,
            remote=remote,
        )
        if delete_tracked_files:
            delete_all_tracked_files(temp_repo)
        # For type narrowing
        if repo.working_dir is None or temp_repo.working_dir is None:
            raise ValueError("repo working dir cannot be None")
        if copy_current_configs:
            copy_flexlate_configs(
                Path(repo.working_dir),
                Path(temp_repo.working_dir),
                Path(repo.working_dir),
            )
        yield temp_repo
        _push_branch_from_one_local_repo_to_another(
            temp_repo, repo, branch_name, force=force_push
        )


def _clone_from_local_repo(
    repo: Repo,
    out_dir: Path,
    branch_name: str,
    base_branch_name: str,
    additional_branches: Sequence[str] = tuple(),
    remote: str = "origin",
) -> Repo:
    if additional_branches:
        return _clone_specific_branches_from_local_repo(
            repo,
            out_dir,
            [branch_name, *additional_branches],
            branch_name,
            base_branch_name,
            remote=remote,
        )
    return _clone_single_branch_from_local_repo(
        repo, out_dir, branch_name, base_branch_name, remote=remote
    )


def _clone_single_branch_from_local_repo(
    repo: Repo,
    out_dir: Path,
    branch_name: str,
    base_branch_name: str,
    remote: str = "origin",
) -> Repo:
    use_branch_name = branch_name
    if not branch_exists(repo, branch_name):
        # Branch doesn't exist, instead clone either the base branch or the current one
        # Will need to do the checkout later after adding files
        _update_local_branch_from_remote_without_checkout(
            repo, base_branch_name, remote=remote
        )
        if branch_exists(repo, base_branch_name):
            use_branch_name = base_branch_name
        else:
            use_branch_name = repo.active_branch.name

    # Branch exists, clone only that branch
    repo.git.clone(
        repo.working_dir, "--branch", use_branch_name, "--single-branch", out_dir
    )
    temp_repo = Repo(out_dir)

    if not branch_exists(temp_repo, branch_name):
        # Now create the new branch
        checkout_template_branch(temp_repo, branch_name, base_branch_name)

    return temp_repo


def _clone_specific_branches_from_local_repo(
    repo: Repo,
    out_dir: Path,
    branch_names: Sequence[str],
    checkout_branch: str,
    base_checkout_branch: str,
    remote: str = "origin",
) -> Repo:
    temp_repo = Repo.init(out_dir)
    valid_branches = [name for name in branch_names if branch_exists(repo, name)]
    branch_arguments = list(
        itertools.chain(*[["-t", branch] for branch in valid_branches])
    )
    temp_repo.git.remote("add", "-f", *branch_arguments, "origin", repo.working_dir)
    for branch in valid_branches:
        # TODO: is there a way to set up remote tracking branches without checkout?
        temp_repo.git.checkout("-t", f"origin/{branch}")

    if branch_exists(repo, checkout_branch):
        temp_repo.branches[checkout_branch].checkout()  # type: ignore
    else:
        # Create the branch
        _update_local_branch_from_remote_without_checkout(
            repo, base_checkout_branch, remote=remote
        )
        checkout_template_branch(repo, checkout_branch, base_checkout_branch)
    return temp_repo


def _update_local_branch_from_remote_without_checkout(
    repo: Repo, branch_name: str, remote: str = "origin"
):
    try:
        repo.git.fetch(remote, f"{branch_name}:{branch_name}")
    except GitCommandError as e:
        if "couldn't find remote ref" in str(e):
            # No remote branch, so this is a no-op
            return
        if "non-fast-forward" in str(e):
            # The local branch is ahead of the remote branch,
            # so this is a no-op
            return
        if "Could not read from remote repository" in str(e):
            # There is likely not a remote for this repo. If there is,
            # it has a different name than what was passed
            return
        # Unknown git error, raise it
        raise e


def update_local_branches_from_remote_without_checkout(
    repo: Repo, branch_names: Sequence[str], remote: str = "origin"
):
    for branch in branch_names:
        _update_local_branch_from_remote_without_checkout(repo, branch, remote)


def _push_branch_from_one_local_repo_to_another(
    from_repo: Repo, to_repo: Repo, branch_name: str, force: bool = False
):
    args: Tuple[str, ...]
    if force:
        args = ("--force", str(to_repo.working_dir), branch_name)
    else:
        args = (str(to_repo.working_dir), branch_name)
    from_repo.git.push(*args)


def branch_exists(repo: Repo, branch_name: str) -> bool:
    try:
        repo.branches[branch_name]  # type: ignore
        return True
    except IndexError:
        return False


@contextmanager
def checked_out_template_branch(repo: Repo, branch_name: str, base_branch_name: str):
    orig_branch = repo.active_branch
    checkout_template_branch(
        repo, branch_name=branch_name, base_branch_name=base_branch_name
    )
    yield
    orig_branch.checkout()


def repo_has_merge_conflicts(repo: Repo) -> bool:
    for path, blob_tuples in repo.index.unmerged_blobs().items():
        for (code, blob) in blob_tuples:
            if code != 0:
                # Code 0 means merged successfully. 1, 2, and 3 represent conflicts
                return True
    return False


def assert_repo_is_in_clean_state(repo: Repo):
    if repo.is_dirty(untracked_files=True):
        raise GitRepoDirtyException(
            "git working tree is not clean. Please commit, stash, or discard any changes first."
        )
    if "unknown revision" in repo.git.rev_parse("HEAD"):
        # Empty repo, no commits
        raise GitRepoHasNoCommitsException(
            "git repo has no commits. Please initialize it with a commit"
        )


def get_repo_remote_name_from_repo(repo: Repo) -> str:
    url = list(repo.remote().urls)[0]
    parts = url.split("/")
    name_part = parts[-1]
    # Remove .git on end if it exists
    if ".git" in name_part:
        return ".".join(name_part.split(".")[:-1])
    # Otherwise return name as-is
    return name_part


def clone_repo_at_version_get_repo_and_name(
    path: str, dst_folder: Path, version: Optional[str] = None
) -> Tuple[Repo, str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        repo = Repo.clone_from(path, temp_dir)
        name = get_repo_remote_name_from_repo(repo)
        if version:
            checkout_version(repo, version)
        else:
            version = get_current_version(repo)
        template_root = dst_folder / name
        full_destination = template_root / version
        if not template_root.exists():
            template_root.mkdir(parents=True)
        if not full_destination.exists():
            # Have not cloned this version previously
            shutil.copytree(temp_dir, full_destination)
    return Repo(full_destination), name


def checkout_version(repo: Repo, version: str):
    repo.git.checkout(version)


def reset_current_branch_to_commit(repo: Repo, commit: Commit):
    commit_sha = commit.hexsha
    repo.git.reset("--hard", commit_sha)


def get_commits_between_two_commits(
    repo: Repo, start: Commit, end: Commit
) -> List[Commit]:
    raw_commit_output = repo.git.rev_list(
        "--ancestry-path", f"{start.hexsha}..{end.hexsha}"
    )
    commit_shas = raw_commit_output.split("\n")
    return [repo.commit(sha) for sha in commit_shas]


def push_to_remote(repo: Repo, branch_name: str, remote_name: str = "origin"):
    repo.git.push("-u", remote_name, f"{branch_name}:{branch_name}")


def get_merge_conflict_diffs(repo: Repo) -> str:
    return repo.git.diff("--diff-filter=U")
