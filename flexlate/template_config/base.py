import abc

from flexlate.template_data import TemplateData


class TemplateConfig(abc.ABC):

    def __init__(self, defaults: TemplateData):
        self.defaults = defaults