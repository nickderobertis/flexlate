import abc

from flexlate.template_data import TemplateData


class TemplateConfig(abc.ABC):
    def __init__(self, defaults: TemplateData):
        self.defaults = defaults

    def __eq__(self, other):
        try:
            return all([self.defaults == other.defaults])
        except AttributeError:
            return False
