from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
import uuid
from typing import Any, Dict, Optional, Type, List, Union
from functools import lru_cache

register = template.Library()


class Prop:
    def __init__(self, type: Union[Type, tuple], default: Any = None, required: bool = False, choices: Optional[List] = None):
        self.type = type
        self.default = default
        self.required = required
        self.choices = choices

    def validate(self, value: Any, name: str) -> Any:
        if value is None and self.required:
            raise ValueError(f"Prop '{name}' is required")
        if value is not None and not isinstance(value, self.type):
            raise ValueError(f"Prop '{name}' must be of type {
                             self.type.__name__}")
        if self.choices and value not in self.choices:
            raise ValueError(f"Prop '{name}' must be one of {self.choices}")
        return value if value is not None else self.default


class Component:
    template: str = ""
    styles: str = ""
    scripts: str = ""
    props: Dict[str, Prop] = {}
    static_bundle: str = ""

    def __init__(self, **kwargs):
        self.id = f"djuno-{uuid.uuid4().hex[:8]}"
        self.kwargs = self.validate_props(kwargs)
        self.template_obj = self.compile_template()

    def validate_props(self, kwargs: Dict) -> Dict:
        validated = {}
        for name, prop in self.props.items():
            validated[name] = prop.validate(kwargs.get(name), name)
        for key in kwargs:
            if key not in self.props:
                raise ValueError(f"Unknown prop '{key}' for component {
                                 self.__class__.__name__}")
        return validated

    @lru_cache(maxsize=100)
    def compile_template(self):
        return template.Template(self.template)

    def get_context_data(self) -> Dict:
        return {**self.kwargs, 'id': self.id}

    def render(self) -> str:
        context = template.Context(self.get_context_data())
        html = self.template_obj.render(context)
        static_tag = f'<link rel="stylesheet" href="{
            static(self.static_bundle)}">' if self.static_bundle else ''
        return mark_safe(f"{static_tag}\n{html}")


@register.tag
def component(parser, token):
    tag_name, component_name, *args = token.split_contents()
    kwargs = {}
    for arg in args:
        key, value = arg.split('=')
        kwargs[key.strip()] = value.strip('"\'')
    nodelist = parser.parse(('endcomponent',))
    parser.delete_first_token()
    return ComponentNode(component_name.strip('"\''), kwargs, nodelist)


class ComponentNode(template.Node):
    def __init__(self, component_name: str, kwargs: Dict, nodelist):
        self.component_name = component_name
        self.kwargs = kwargs
        self.nodelist = nodelist

    def render(self, context):
        component_class = component_registry.get(self.component_name)
        if not component_class:
            raise template.TemplateSyntaxError(
                f"Component '{self.component_name}' not found")
        component = component_class(**self.kwargs)
        context['slot_content'] = self.nodelist.render(context)
        return component.render()


component_registry = {}


def register_component(name: str):
    def decorator(cls):
        component_registry[name] = cls
        return cls
    return decorator


def parse_djuno_file(filepath: str) -> Dict[str, str]:
    with open(filepath, 'r') as f:
        content = f.read()
    sections = {'template': '', 'styles': '', 'scripts': ''}
    current_section = None
    for line in content.split('\n'):
        if line.strip() in ['--- template ---', '--- styles ---', '--- scripts ---']:
            current_section = line.strip()[4:-4].strip()
        elif current_section:
            sections[current_section] += line + '\n'
    return sections
