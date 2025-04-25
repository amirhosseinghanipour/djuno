from djuno.component import Component, Prop, register_component, parse_djuno_file
from django.conf import settings
import os


@register_component('modal')
class Modal(Component):
    props = {
        'title': Prop(str, default=""),
        'content': Prop(str, default=""),
        'footer': Prop(str, default=""),
        'size': Prop(str, default="lg", choices=["sm", "lg"]),
        'open': Prop(bool, default=False),
        'js': Prop(str, default="none", choices=["none", "alpine", "htmx"])
    }
    static_bundle = "components/modal.bundle.css"

    def __init__(self, **kwargs):
        djuno_file = os.path.join(
            settings.BASE_DIR, 'components', 'modal', 'modal.djuno')
        sections = parse_djuno_file(djuno_file)
        self.template = sections['template']
        self.styles = sections['styles']
        self.scripts = sections['scripts']
        super().__init__(**kwargs)

    def get_context_data(self):
        js_attrs = ""
        if self.kwargs['js'] == "alpine":
            js_attrs = 'x-data="{ open: {{ open|lower }} }" x-show="open"'
        elif self.kwargs['js'] == "htmx":
            js_attrs = 'hx-post="/modal/" hx-swap="outerHTML"'
        return {
            **super().get_context_data(),
            'class': f"{'hidden' if not self.kwargs['open'] else ''} {self.kwargs['size']}",
            'js_attrs': js_attrs
        }
