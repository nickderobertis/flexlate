class FlexlateException(Exception):
    pass


class RendererNotFoundException(FlexlateException):
    pass


class InvalidTemplateClassException(FlexlateException):
    pass


class FlexlateGitException(FlexlateException):
    pass


class GitRepoDirtyException(FlexlateGitException):
    pass
