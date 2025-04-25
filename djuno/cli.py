import click
import os
from pathlib import Path
import subprocess


@click.group()
def cli():
    pass


@cli.command()
def init():
    """Initialize a Djuno project."""
    click.echo("Setting up Djuno project...")
    Path('components').mkdir(exist_ok=True)
    Path('static/components').mkdir(parents=True, exist_ok=True)
    Path('templates').mkdir(exist_ok=True)
    Path('tests').mkdir(exist_ok=True)
    subprocess.run(['npm', 'install', '-D', 'tailwindcss', 'esbuild'])
    with open('package.json', 'w') as f:
        f.write('{"scripts": {"build": "esbuild components/*.djuno --bundle --outdir=static/components --loader:.djuno=css"}}')
    click.echo("Djuno initialized! Run `npm run build` to bundle assets.")


@cli.command()
@click.argument('name')
@click.option('--js', default='none', type=click.Choice(['none', 'alpine', 'htmx']), prompt='JavaScript framework?')
def add(name):
    """Generate a new component."""
    component_dir = Path('components') / name
    component_dir.mkdir(exist_ok=True)
    djuno_file = component_dir / f"{name}.djuno"
    py_file = component_dir / f"{name}.py"

    djuno_content = f"""
--- template ---
<div class="{{{{ id }}}} {{{{ class }}}}" {{{{ js_attrs }}}}
    {{% slot content %}}
        {{{{ text }}}}
    {{% endslot %}}
</div>

--- styles ---
.{{{{ id }}}}.default {{ @apply bg-gray-100 p-4; }}

--- scripts ---
{ % if js == "alpine" % }
document.addEventListener('alpine:init', () => {{
    Alpine.data('{name}', () => ({{}}));
}});
{ % endif % }
"""

    py_content = f"""
from djuno.component import Component, Prop, register_component, parse_djuno_file
from django.conf import settings
import os

@register_component('{name}')
class {name.capitalize()}(Component):
    props = {{
        'text': Prop(str, default="Click Me"),
        'class': Prop(str, default="default"),
        'js': Prop(str, default="{js}", choices=["none", "alpine", "htmx"])
    }}
    static_bundle = "components/{name}.bundle.css"

    def __init__(self, **kwargs):
        djuno_file = os.path.join(
            settings.BASE_DIR, 'components', '{name}', '{name}.djuno')
        sections = parse_djuno_file(djuno_file)
        self.template = sections['template']
        self.styles = sections['styles']
        self.scripts = sections['scripts']
        super().__init__(**kwargs)

    def get_context_data(self):
        js_attrs = ""
        if self.kwargs['js'] == "alpine":
            js_attrs = 'x-data="{{{{ id }}}}"'
        elif self.kwargs['js'] == "htmx":
            js_attrs = 'hx-post="/toggle/" hx-swap="outerHTML"'
        return {{
            **super().get_context_data(),
            'js_attrs': js_attrs
        }}
"""

    with open(djuno_file, 'w') as f:
        f.write(djuno_content)
    with open(py_file, 'w') as f:
        f.write(py_content)

    subprocess.run(['npm', 'run', 'build'])

    click.echo(f"Component '{name}' created at {component_dir}")


if __name__ == '__main__':
    cli()
