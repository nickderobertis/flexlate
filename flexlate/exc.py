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


class FlexlateGitException(FlexlateException):
    pass


class GitRepoDirtyException(FlexlateGitException):
    pass


class FlexlateConfigException(FlexlateException):
    pass


class FlexlateConfigFileNotExistsException(FlexlateConfigException):
    pass