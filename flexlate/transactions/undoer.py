from git import Repo

from flexlate.ext_git import assert_repo_is_in_clean_state


class Undoer:
    def undo_transaction(self, repo: Repo):
        assert_repo_is_in_clean_state(repo)
        if repo.working_dir is None:
            raise ValueError("repo working dir should not be none")
        breakpoint()

    def undo_transactions(self, repo: Repo, num_transactions: int = 1):
        for _ in range(num_transactions):
            self.undo_transaction(repo)
