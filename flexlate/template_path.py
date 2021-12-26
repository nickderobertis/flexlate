import re
from pathlib import Path

REPO_REGEX = re.compile(
    r"""
# something like git:// ssh:// file:// etc.
((((git|hg)\+)?(git|ssh|file|https?):(//)?)
 |                                      # or
 (\w+@[\w.]+)                          # something like user@...
)
""",
    re.VERBOSE,
)


def is_repo_url(value):
    """Return True if value is a repository URL."""
    return bool(REPO_REGEX.match(value))

def is_local_template(path: str) -> bool:
    return Path(path).exists()

