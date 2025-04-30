from django import template
from typing import Dict, Any, Optional, Type, Union
from .compiler import parse_dj_file
from .registry import register_component
from pathlib import Path


class Prop:
    def __init__(
        self,
        type_: Type,
        default: Any = None,
        required: bool = False,
        choices: Optional[list] = None
    ):
        self.type_ = type_
        self.default = default
        self.required = required
        self.choices = choices

    def validate(self, value: Any, key: str) -> Any:
        if value is None and self.required:
            raise ValueError(f"Prop '{key}' is required")
        if value is not None:
            if self.choices and value not in self.choices:
                raise ValueError(f"Invalid value for {key}: {value}")
            return self.type_(value)
        return self.default


class Component:
    props: Dict[str, Prop] = {}
    template: str = ''
    styles: Dict[str, str] = {}
    scripts: str = ''
    slots: Dict[str, str] = {}

    def __init__(self, slots: Dict[str, str] = None, **kwargs):
        self.kwargs = {}
        self.slots = slots or {'default': ''}
        for key, prop in self.props.items():
            value = kwargs.get(key)
            self.kwargs[key] = prop.validate(value, key)

    def get_context_data(self) -> Dict[str, Any]:
        context = {
            'id': self.kwargs.get('id'),
            'class': self.kwargs.get('class', 'default'),
            'styles': self.styles,
            'hydration': self.get_hydration_data(),
            **self.kwargs
        }
        for slot_name, slot_content in self.slots.items():
            context[slot_name] = slot_content
        return context

    def get_hydration_data(self) -> str:
        if self.kwargs.get('js') == 'alpine':
            return '<script>document.addEventListener("alpine:init", () => { Alpine.hydrate(this); });</script>'
        return ''

    def render(self) -> str:
        t = template.Template(self.template)
        c = template.Context(self.get_context_data())
        return t.render(c)


def from_dj_file(file_path: str) -> Type[Component]:
    sections = parse_dj_file(file_path)
    name = Path(file_path).stem

    class DynamicComponent(Component):
        template = sections['template']
        styles = {'default': f'{name}_default_abc123'}
        scripts = sections['script']

        props = {
            'id': Prop(str, default=None),
            'text': Prop(str, default='Click Me', required=(name == 'button')),
            'name': Prop(str, default='star', required=(name == 'icon')),
            'class': Prop(str, default='default'),
            'js': Prop(str, default='none', choices=['none', 'alpine', 'htmx']),
            'disabled': Prop(bool, default=False),
            'icon': Prop(str, default=None)
        }

    register_component(name, DynamicComponent)
    return DynamicComponent
