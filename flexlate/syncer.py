from git import Repo

from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_TEMPLATE_BRANCH_NAME, DEFAULT_MERGED_BRANCH_NAME
from flexlate.render.multi import MultiRenderer
from flexlate.transactions.transaction import FlexlateTransaction
from flexlate.update.main import Updater


class Syncer:
    def sync_local_changes_to_flexlate_branches(
        self,
        repo: Repo,
        transaction: FlexlateTransaction,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        no_input: bool = False,
        quiet: bool = False,
        updater: Updater = Updater(),
        renderer: MultiRenderer = MultiRenderer(),
        config_manager: ConfigManager = ConfigManager(),
    ):
        updater.update(
            repo,
            [],
            transaction,
            merged_branch_name=merged_branch_name,
            template_branch_name=template_branch_name,
            no_input=no_input,
            quiet=quiet,
            full_rerender=True,
            renderer=renderer,
            config_manager=config_manager,
        )
