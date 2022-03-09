class FlexlateException(Exception):
    pass


class RendererNotFoundException(FlexlateException):
    pass


class FlexlateTemplateException(FlexlateException):
    pass


class InvalidTemplateClassException(FlexlateTemplateException):
    pass


class InvalidTemplateTypeException(FlexlateTemplateException):
    pass


class InvalidTemplatePathException(FlexlateTemplateException):
    pass


class TemplateLookupException(FlexlateTemplateException):
    pass


class InvalidTemplateDataException(FlexlateTemplateException):
    pass


class TemplateNotRegisteredException(FlexlateTemplateException):
    pass


class CannotFindTemplateSourceException(FlexlateTemplateException):
    pass


class CannotFindAppliedTemplateException(FlexlateTemplateException):
    pass


class CannotFindClonedTemplateException(FlexlateTemplateException):
    pass


class TemplateSourceWithNameAlreadyExistsException(FlexlateTemplateException):
    pass


class FlexlateGitException(FlexlateException):
    pass


class GitRepoDirtyException(FlexlateGitException):
    pass


class GitRepoHasNoCommitsException(FlexlateGitException):
    pass


class TriedToCommitButNoChangesException(FlexlateGitException):
    pass


class FlexlateConfigException(FlexlateException):
    pass


class CannotLoadConfigException(FlexlateConfigException):
    pass


class CannotRemoveConfigItemException(FlexlateConfigException):
    pass


class CannotRemoveTemplateSourceException(CannotRemoveConfigItemException):
    pass


class CannotRemoveAppliedTemplateException(CannotRemoveConfigItemException):
    pass


class FlexlateConfigFileNotExistsException(CannotLoadConfigException):
    pass


class FlexlateProjectConfigFileNotExistsException(CannotLoadConfigException):
    pass


class FlexlateTransactionException(FlexlateException):
    pass


class CannotParseCommitMessageFlexlateTransaction(FlexlateTransactionException):
    pass


class LastCommitWasNotByFlexlateException(FlexlateTransactionException):
    pass


class TransactionMismatchBetweenBranchesException(FlexlateTransactionException):
    pass


class TooFewTransactionsException(FlexlateTransactionException):
    pass


class InvalidNumberOfTransactionsException(FlexlateTransactionException):
    pass


class ExpectedMergeCommitException(FlexlateTransactionException):
    pass


class CannotFindCorrectMergeParentException(FlexlateTransactionException):
    pass


class UserChangesWouldHaveBeenDeletedException(FlexlateTransactionException):
    pass


class MergeCommitIsNotMergingAFlexlateTransactionException(
    FlexlateTransactionException
):
    pass


class CannotFindMergeForTransactionException(FlexlateTransactionException):
    pass


class FlexlateSyncException(FlexlateException):
    pass


class UnnecessarySyncException(FlexlateSyncException):
    pass


class FlexlateUpdateException(FlexlateException):
    pass


class MergeConflictsAndAbortException(FlexlateException):
    pass
