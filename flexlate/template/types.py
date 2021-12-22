from enum import Enum


class TemplateType(str, Enum):
    BASE = "base, should be overriden"
    COOKIECUTTER = "cookiecutter"
    COPIER = "copier"
