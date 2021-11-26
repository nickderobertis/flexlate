import abc

from flexlate.types import TemplateData


class TemplateConfig(abc.ABC):

    def __init__(self, defaults: TemplateData):
        self.defaults = defaults