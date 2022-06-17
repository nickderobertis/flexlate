import os
import platform
import shutil
from pathlib import Path
from typing import Literal

import nox

nox.options.sessions = ["format", "strip", "lint", "test"]

VENVS_DIR = Path("~").expanduser() / ".venvs"
PROJECT_NAME = Path(__file__).parent.name
PROJECT_VENV_DIR = VENVS_DIR / PROJECT_NAME
LINT_VENV_DIR = PROJECT_VENV_DIR / "lint"
LINT_VENV_DIR_STR = str(LINT_VENV_DIR)

VenvName = Literal["lint"]


@nox.session(python=False)
def format(session):
    if session.posargs:
        files = session.posargs
    else:
        files = ["."]

    if session.interactive:
        # When run as user, format the files in place
        _format_in_place(session, files)
    else:
        # When run from CI, fail the check if formatting is not correct
        session.run("isort", "--check-only", *files)
        session.run("black", "--check", *files)


@nox.session(python=False)
def format_files(session):
    if session.posargs:
        files = session.posargs
    else:
        files = ["."]

    _format_in_place(session, files)


def _format_in_place(session, files):
    session.run("isort", *files)
    session.run("black", *files)


@nox.session(python=False)
def lint(session):
    _setup_venv(session, "lint")

    def run_lint(*args):
        _run_in_venv(session, "lint", *args)

    run_lint(
        "flake8", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"
    )
    run_lint(
        "flake8",
        "--count",
        "--exit-zero",
        "--max-complexity=10",
        "--max-line-length=127",
        "--statistics",
    )
    run_lint("mypy")


@nox.session(python=False, name="strip")
def strip_imports(session):
    common_args = (
        "--remove-all-unused-imports",
        "--in-place",
        "--recursive",
        ".",
        "--exclude=test*,__init__.py",
    )
    if session.interactive:
        # When run as user, strip unused imports and exit successfully
        session.run("autoflake", *common_args)
    else:
        # When run from CI, fail the check if stripping is not correct
        session.run("autoflake", "--check", *common_args)


@nox.session
def test(session):
    session.install(
        "-r", "test-requirements.txt", "--upgrade", "--upgrade-strategy", "eager"
    )
    session.install(".")
    session.run("pytest", *session.posargs)


@nox.session
def test_coverage(session):
    session.install(
        "-r", "test-requirements.txt", "--upgrade", "--upgrade-strategy", "eager"
    )
    session.install(".")
    session.run("pytest", "--cov=./", "--cov-report=xml")


@nox.session(python=False)
def docs(session):
    session.chdir("docsrc")
    session.run("make", "github")
    if session.interactive:
        session.run("bash", "./dev-server.sh")


def _setup_venv(session, venv_name: VenvName):
    venv_path = _venv_path(venv_name)
    if _venv_exists(venv_name):
        print(f"Using existing {venv_name} venv at {venv_path}")
        return
    session.run("virtualenv", str(venv_path))
    _update_venv(session, venv_name)


def _venv_path(venv_name: VenvName) -> Path:
    return PROJECT_VENV_DIR / venv_name


def _venv_exists(venv_name: VenvName):
    venv_dir = _venv_path(venv_name)
    return venv_dir.exists()


@nox.session(python=False)
def venv(session):
    # First argument is one of "delete", "update", "create"
    # Second argument is the name of the venv
    if len(session.posargs) < 2:
        raise ValueError(
            f"Must supply first action (delete, update, create), then venv name, got {session.posargs}"
        )
    action = session.posargs[0]
    venv_name = session.posargs[1]
    if action == "delete":
        _delete_venv(venv_name)
    elif action == "update":
        _update_venv(session, venv_name)
    elif action == "create":
        _setup_venv(session, venv_name)
    else:
        raise ValueError(f"Action must be delete or update, got {action}")


def _run_in_venv(session, venv_name: VenvName, *args):
    new_command = _venv_command(venv_name, *args)
    session.run(*new_command)


def _venv_command(venv_name: VenvName, *args):
    if platform.system() == "Windows":
        return _venv_command_windows(venv_name, *args)
    return _venv_command_unix(venv_name, *args)


def _venv_command_unix(venv_name: VenvName, *args):
    venv_dir = _venv_path(venv_name)
    venv_command = os.path.sep.join((str(venv_dir), "bin", args[0]))
    new_args = [venv_command, *args[1:]]
    return new_args


def _venv_command_windows(venv_name: VenvName, *args):
    venv_dir = _venv_path(venv_name)
    venv_command = os.path.sep.join((str(venv_dir), "Scripts", args[0] + ".exe"))
    new_args = [venv_command, *args[1:]]
    return new_args


def _delete_venv(venv_name: VenvName):
    venv_dir = _venv_path(venv_name)
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
        print(f"Deleted venv {venv_name} from {venv_dir}")
    else:
        raise ValueError(f"Venv {venv_name} does not exist at {venv_dir}")


def _update_venv(session, venv_name: VenvName):
    venv_dir = _venv_path(venv_name)
    if not venv_dir.exists():
        raise ValueError(
            f"Venv {venv_name} does not exist at {venv_dir}, cannot update"
        )
    _run_in_venv(
        session, venv_name, "pip", "install", "-r", f"{venv_name}-requirements.txt"
    )
