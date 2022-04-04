from git import Repo

from flexlate import exc
from flexlate.config_manager import ConfigManager
from flexlate.constants import DEFAULT_TEMPLATE_BRANCH_NAME, DEFAULT_MERGED_BRANCH_NAME
from flexlate.render.multi import MultiRenderer
from flexlate.styles import print_styled, INFO_STYLE, SUCCESS_STYLE
from flexlate.transactions.transaction import FlexlateTransaction
from flexlate.update.main import Updater


class Syncer:
    def sync_local_changes_to_flexlate_branches(
        self,
        repo: Repo,
        transaction: FlexlateTransaction,
        merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        base_merged_branch_name: str = DEFAULT_MERGED_BRANCH_NAME,
        template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        base_template_branch_name: str = DEFAULT_TEMPLATE_BRANCH_NAME,
        no_input: bool = False,
        remote: str = "origin",
        updater: Updater = Updater(),
        renderer: MultiRenderer = MultiRenderer(),
        config_manager: ConfigManager = ConfigManager(),
    ):
        print_styled("Syncing local changes to flexlate branches", INFO_STYLE)
        try:
            updater.update(
                repo,
                [],
                transaction,
                merged_branch_name=merged_branch_name,
                base_merged_branch_name=base_merged_branch_name,
                template_branch_name=template_branch_name,
                base_template_branch_name=base_template_branch_name,
                no_input=no_input,
                full_rerender=True,
                remote=remote,
                renderer=renderer,
                config_manager=config_manager,
            )
        except exc.TriedToCommitButNoChangesException as e:
            raise exc.UnnecessarySyncException("Everything is up to date") from e
        print_styled(
            "Successfully synced local changes to flexlate branches", SUCCESS_STYLE
        )
