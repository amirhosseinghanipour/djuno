import click
import os
from pathlib import Path
import subprocess
import ast


def find_settings_path(project_name):
    """Find the Django settings.py file in the project."""
    return Path(project_name) / f"{project_name}/settings.py"


def check_settings(project_name):
    """Check settings.py for required Djuno configurations."""
    settings_path = find_settings_path(project_name)
    results = {
        'INSTALLED_APPS': False,
        'TEMPLATES': False,
        'STATICFILES_DIRS': False,
        'STATIC_URL': False,
        'SECRET_KEY': False
    }
    instructions = []

    if not settings_path.exists():
        instructions.append("⚠️ No settings.py found. Please configure:")
        instructions.extend([
            "  - INSTALLED_APPS: Include 'djuno':",
            "      INSTALLED_APPS = [..., 'djuno']",
            "  - TEMPLATES: Add 'templates' to DIRS and static context processor:",
            "      TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': ['templates'], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.static']}},]",
            "  - STATICFILES_DIRS: Add 'static':",
            "      STATICFILES_DIRS = ['static']",
            "  - STATIC_URL: Set to '/static/':",
            "      STATIC_URL = '/static/'",
            "  - SECRET_KEY: Set a secure key:",
            "      SECRET_KEY = 'your-secure-key-here'"
        ])
        return results, instructions

    with open(settings_path, 'r') as f:
        content = f.read()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id == 'INSTALLED_APPS':
                                value = ast.literal_eval(node.value)
                                results['INSTALLED_APPS'] = 'djuno' in value
                            elif target.id == 'TEMPLATES':
                                value = ast.literal_eval(node.value)
                                dirs_ok = any(
                                    'DIRS' in t and 'templates' in t['DIRS'] for t in value)
                                ctx_ok = any(
                                    'OPTIONS' in t and 'context_processors' in t['OPTIONS'] and 'django.template.context_processors.static' in t['OPTIONS']['context_processors'] for t in value)
                                results['TEMPLATES'] = dirs_ok and ctx_ok
                            elif target.id == 'STATICFILES_DIRS':
                                value = ast.literal_eval(node.value)
                                results['STATICFILES_DIRS'] = 'static' in value or any(
                                    'static' in str(v) for v in value)
                            elif target.id == 'STATIC_URL':
                                results['STATIC_URL'] = bool(
                                    ast.literal_eval(node.value))
                            elif target.id == 'SECRET_KEY':
                                results['SECRET_KEY'] = bool(
                                    ast.literal_eval(node.value))
        except (SyntaxError, ValueError):
            instructions.append(
                "⚠️ Error parsing settings.py. Manually verify configurations.")

    if not results['INSTALLED_APPS']:
        instructions.extend([
            "  - Add 'djuno' to INSTALLED_APPS:",
            "      INSTALLED_APPS = [..., 'djuno']"
        ])
    if not results['TEMPLATES']:
        instructions.extend([
            "  - Add 'templates' to TEMPLATES['DIRS'] and static context processor:",
            "      TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': ['templates'], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.static']}},]"
        ])
    if not results['STATICFILES_DIRS']:
        instructions.extend([
            "  - Add 'static' to STATICFILES_DIRS:",
            "      STATICFILES_DIRS = ['static']"
        ])
    if not results['STATIC_URL']:
        instructions.extend([
            "  - Set STATIC_URL:",
            "      STATIC_URL = '/static/'"
        ])
    if not results['SECRET_KEY']:
        instructions.extend([
            "  - Set a secure SECRET_KEY:",
            "      SECRET_KEY = 'your-secure-key-here'"
        ])

    return results, instructions


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name', required=False)
def init(name):
    """Initialize a Djuno project with a Django project."""
    click.echo("🚀 Welcome to Djuno!")

    # Prompt for project name if not provided
    if not name:
        name = click.prompt("✨ Project name", default="myproject")

    # Validate project name
    if not name.isidentifier():
        click.echo(
            "❌ Project name must be a valid Python identifier (e.g., myproject).")
        return

    # Check if directory exists
    if Path(name).exists():
        click.echo(f"❌ Directory '{
                   name}' already exists. Choose a different name.")
        return

    # Create Django project
    click.echo(f"✅ Creating Django project '{name}'...")
    subprocess.run(['django-admin', 'startproject', name])

    # Create components directory
    components_dir = Path(name) / 'components' / 'button'
    components_dir.mkdir(parents=True, exist_ok=True)

    # Write sample button.dj
    with open(components_dir / 'button.dj', 'w') as f:
        f.write('''<template>
  <button
    class="{{ class }} default"
    {{ js_attrs }}
    {% if id %}id="{{ id }}"{% endif %}
    {% if disabled %}disabled{% endif %}
  >
    {% if icon %}
      <span class="mr-2">{{ icon }}</span>
    {% endif %}
    <slot name="header"></slot>
    <slot>{{ text }}</slot>
    <slot name="footer"></slot>
  </button>
</template>

<style scoped>
  .default {
    background-color: #f0f0f0;
    padding: 1rem;
    border-radius: 0.25rem;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
  }
  .default:hover {
    background-color: #e0e0e0;
  }
  .disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>

<script lang="ts">
  /**
   * A customizable button component with named slots and icons.
   * @example <button_component text="Click Me"><template slot="header"><icon_component name="star" /></template></button_component>
   */
  export default {
    name: '{{ name }}',
    props: {
      id: { type: String as () => string | null, default: null },
      text: { type: String as () => string, default: 'Click Me', required: true },
      class: { type: String as () => string, default: 'default' },
      js: { type: String as () => 'none' | 'alpine' | 'htmx', default: 'none' },
      disabled: { type: Boolean as () => boolean, default: false },
      icon: { type: String as () => string | null, default: null }
    },
    data(): { isClicked: boolean } {
      return {
        isClicked: false
      };
    },
    computed: {
      js_attrs(): string {
        if (this.js === 'alpine') {
          return `x-data="{ isClicked: ${this.isClicked} }" @click="isClicked = !isClicked" :class="{ 'bg-blue-500 text-white': isClicked }"`;
        }
        if (this.js === 'htmx') {
          return 'hx-post="/toggle/" hx-swap="outerHTML"';
        }
        return '';
      }
    }
  };
</script>
''')

    # Check settings
    click.echo("🔍 Checking Django settings...")
    results, instructions = check_settings(name)
    click.echo("\n📋 Settings status:")
    click.echo(
        f"  ✅ INSTALLED_APPS includes 'djuno'" if results['INSTALLED_APPS'] else f"  ❌ INSTALLED_APPS missing 'djuno'")
    click.echo(
        f"  ✅ TEMPLATES configured" if results['TEMPLATES'] else f"  ❌ TEMPLATES missing configuration")
    click.echo(
        f"  ✅ STATICFILES_DIRS includes 'static'" if results['STATICFILES_DIRS'] else f"  ❌ STATICFILES_DIRS missing 'static'")
    click.echo(
        f"  ✅ STATIC_URL is set" if results['STATIC_URL'] else f"  ❌ STATIC_URL not set")
    click.echo(
        f"  ✅ SECRET_KEY is set" if results['SECRET_KEY'] else f"  ❌ SECRET_KEY not set")

    if instructions:
        click.echo("\n💡 Please configure your settings.py:")
        for instr in instructions:
            click.echo(instr)

    click.echo(f"\n🎉 Djuno initialized in '{name}'!")
    click.echo("Next steps:")
    click.echo(f"  1. cd {name}")
    click.echo("  2. pip install djuno")
    click.echo("  3. python manage.py runserver")
    click.echo(
        "  4. Use components: {% load djuno %}<button_component text=\"Click Me\"></button_component>")


@cli.command()
def check():
    """Check Django settings for Djuno compatibility."""
    click.echo("🔍 Checking Django settings...")
    project_name = os.path.basename(os.getcwd())
    results, instructions = check_settings(project_name)
    click.echo("\n📋 Settings status:")
    click.echo(
        f"  ✅ INSTALLED_APPS includes 'djuno'" if results['INSTALLED_APPS'] else f"  ❌ INSTALLED_APPS missing 'djuno'")
    click.echo(
        f"  ✅ TEMPLATES configured" if results['TEMPLATES'] else f"  ❌ TEMPLATES missing configuration")
    click.echo(
        f"  ✅ STATICFILES_DIRS includes 'static'" if results['STATICFILES_DIRS'] else f"  ❌ STATICFILES_DIRS missing 'static'")
    click.echo(
        f"  ✅ STATIC_URL is set" if results['STATIC_URL'] else f"  ❌ STATIC_URL not set")
    click.echo(
        f"  ✅ SECRET_KEY is set" if results['SECRET_KEY'] else f"  ❌ SECRET_KEY not set")

    if instructions:
        click.echo("\n💡 Please configure your settings.py:")
        for instr in instructions:
            click.echo(instr)
    else:
        click.echo("\n🎉 All settings are configured correctly!")


@cli.command()
@click.argument('name')
@click.option('--template', default='button', help='Template to use (button, icon)')
@click.option('--js', default='none', type=click.Choice(['none', 'alpine', 'htmx']), prompt='JavaScript framework?')
@click.option('--dir', default='components', help='Directory to store components')
def add(name, template, js, dir):
    """Generate a new component in the specified directory."""
    component_dir = Path(dir) / name
    component_dir.mkdir(parents=True, exist_ok=True)
    dj_file = component_dir / f"{name}.dj"

    # Load template from package
    template_path = Path(__file__).parent / 'templates' / f'{template}.dj'
    if not template_path.exists():
        click.echo(f"❌ Template '{template}' not found!")
        return
    with open(template_path) as f:
        content = f.read()

    # Write .dj file
    with open(dj_file, 'w') as f:
        f.write(content.replace('{{ name }}', name))

    click.echo(f"✅ Component '{name}' created at {component_dir}")
    click.echo(
        "💡 Add to your template: {% load djuno %}<button_component text=\"Your Text\"></button_component>")
    click.echo("🔍 Run `djuno check` to verify settings.")


@cli.command()
def docs():
    """Display Djuno documentation."""
    click.echo("""
🚀 Djuno: A Minimal Django Component Library

1. Installation:
   - Run `pip install djuno`
   - Run `djuno init myproject` to create a project
   - Add 'djuno' to INSTALLED_APPS
   - Run `djuno check` to verify settings

2. Creating Components:
   - Run `djuno add button --dir=myapp/components`
   - Use in templates: {% load djuno %}<button_component text="Click Me"></button_component>

3. Running the Project:
   - cd myproject
   - python manage.py runserver
""")


if __name__ == '__main__':
    cli()
