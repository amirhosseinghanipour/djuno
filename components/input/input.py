from djuno.component import Component, Prop, register_component, parse_djuno_file
from django.conf import settings
import os


@register_component('input')
class Input(Component):
    props = {
        'value': Prop(str, default=""),
        'placeholder': Prop(str, default=""),
        'variant': Prop(str, default="default", choices=["default", "error"]),
        'size': Prop(str, default="lg", choices=["sm", "lg"]),
        'disabled': Prop(bool, default=False),
        'js': Prop(str, default="none", choices=["none", "alpine", "htmx"])
    }
    static_bundle = "components/input.bundle.css"

    def __init__(self, **kwargs):
        djuno_file = os.path.join(
            settings.BASE_DIR, 'components', 'input', 'input.djuno')
        sections = parse_djuno_file(djuno_file)
        self.template = sections['template']
        self.styles = sections['styles']
        self.scripts = sections['scripts']
        super().__init__(**kwargs)

    def get_context_data(self):
        js_attrs = ""
        if self.kwargs['js'] == "alpine":
            js_attrs = 'x-model="value"'
        elif self.kwargs['js'] == "htmx":
            js_attrs = 'hx-post="/update/" hx-swap="outerHTML"'
        return {
            **super().get_context_data(),
            'class': f"{self.kwargs['variant']} {self.kwargs['size']}",
            'js_attrs': js_attrs
        }
