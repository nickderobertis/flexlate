import abc

from flexlate.template.base import Template


class TemplateRenderer(abc.ABC):

    def render(self, template: Template):
        ...