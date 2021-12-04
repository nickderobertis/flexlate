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


class FlexlateGitException(FlexlateException):
    pass


class GitRepoDirtyException(FlexlateGitException):
    pass


class GitRepoHasNoCommitsException(FlexlateGitException):
    pass


class FlexlateConfigException(FlexlateException):
    pass


class CannotLoadConfigException(FlexlateConfigException):
    pass


class FlexlateConfigFileNotExistsException(CannotLoadConfigException):
    pass


class FlexlateProjectConfigFileNotExistsException(CannotLoadConfigException):
    pass
