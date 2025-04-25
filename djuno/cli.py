import click
from pathlib import Path
import subprocess
from concurrent.futures import ProcessPoolExecutor
import re


def is_django_project():
    """Check if the current directory is a Django project."""
    return (Path('manage.py').exists() and
            Path('djuno_project/settings.py').exists())


def update_settings():
    """Update Django settings.py with Djuno configuration."""
    settings_path = Path('djuno_project/settings.py')
    if not settings_path.exists():
        return

    with open(settings_path, 'r') as f:
        content = f.read()

    # Add Djuno to INSTALLED_APPS if not present
    if 'djuno' not in content:
        content = re.sub(
            r'INSTALLED_APPS = \[\n(.*?)\]',
            r'INSTALLED_APPS = [\n\1    "djuno",\n    "components",\n]',
            content,
            flags=re.DOTALL
        )

    # Ensure STATICFILES_DIRS is set
    if 'STATICFILES_DIRS' not in content:
        content += '\nSTATICFILES_DIRS = ["static"]\nSTATIC_URL = "/static/"\n'

    with open(settings_path, 'w') as f:
        f.write(content)


@click.group()
def cli():
    pass


@cli.command()
def init():
    """Initialize a Djuno project with zero-config mode."""
    click.echo("Setting up Djuno project...")

    # Detect Django project
    if is_django_project():
        click.echo(
            "Detected existing Django project. Applying zero-config mode...")
        update_settings()
    else:
        click.echo("Creating new Django project structure...")
        Path('djuno_project').mkdir(exist_ok=True)
        with open('djuno_project/__init__.py', 'w') as f:
            f.write('')
        with open('djuno_project/settings.py', 'w') as f:
            f.write('''INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'djuno',
    'components',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.static',
            ],
        },
    },
]

STATICFILES_DIRS = ['static']
STATIC_URL = '/static/'
''')
        with open('djuno_project/urls.py', 'w') as f:
            f.write('''from django.urls import path
from .views import index

urlpatterns = [
    path('', index, name='index'),
]
''')
        with open('djuno_project/views.py', 'w') as f:
            f.write('''from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {})
''')
        with open('djuno_project/wsgi.py', 'w') as f:
            f.write('''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djuno_project.settings')
application = get_wsgi_application()
''')
        with open('manage.py', 'w') as f:
            f.write('''#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djuno_project.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
''')

    # Create directories
    Path('components').mkdir(exist_ok=True)
    Path('static/vite').mkdir(parents=True, exist_ok=True)
    Path('templates').mkdir(exist_ok=True)
    Path('tests').mkdir(exist_ok=True)
    Path('djuno/templates').mkdir(parents=True, exist_ok=True)
    Path('djuno/vite').mkdir(exist_ok=True)
    Path('djuno/cache/components').mkdir(parents=True, exist_ok=True)
    Path('.storybook').mkdir(exist_ok=True)

    # Install Node dependencies
    subprocess.run(['npm', 'install', '-D', 'vite', 'vite-plugin-django', 'tailwindcss', 'postcss', '@storybook/html', '@storybook/addon-essentials',
                   '@storybook/addon-controls', 'jest', '@testing-library/jest-dom', 'typescript', 'eslint', '@typescript-eslint/parser', '@typescript-eslint/eslint-plugin'])

    # Write package.json
    with open('package.json', 'w') as f:
        f.write('''{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build",
    "test": "jest",
    "lint": "eslint components/**/*.{js,ts} --fix"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "vite-plugin-django": "^1.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "@storybook/html": "^8.0.0",
    "@storybook/addon-essentials": "^8.0.0",
    "@storybook/addon-controls": "^8.0.0",
    "jest": "^29.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0"
  }
}''')

    # Write vite.config.ts
    with open('vite.config.ts', 'w') as f:
        f.write('''import { defineConfig } from 'vite';
import django from 'vite-plugin-django';
import djuno from './djuno/vite/plugin-djuno';

export default defineConfig({
  plugins: [django(), djuno()],
  css: {
    modules: {
      generateScopedName: '[name]_[local]_[hash:base64:5]'
    }
  },
  build: {
    outDir: 'static/vite',
    rollupOptions: {
      input: 'components/*/*.dj'
    }
  }
});
''')

    # Write tsconfig.json
    with open('tsconfig.json', 'w') as f:
        f.write('''{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["components/**/*.{js,ts}", "djuno/vite/**/*.{js,ts}", ".storybook/**/*.{js,ts}"]
}
''')

    # Write Storybook config
    with open('.storybook/main.ts', 'w') as f:
        f.write('''import type { StorybookConfig } from '@storybook/html-vite';

const config: StorybookConfig = {
  stories: ['../components/**/*.stories.ts'],
  addons: ['@storybook/addon-essentials', '@storybook/addon-controls'],
  framework: {
    name: '@storybook/html-vite',
    options: {}
  }
};

export default config;
''')

    with open('.storybook/preview.ts', 'w') as f:
        f.write('''import type { Preview } from '@storybook/html';

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/
      }
    }
  }
};

export default preview;
''')

    # Write Tailwind config
    with open('tailwind.config.js', 'w') as f:
        f.write('''module.exports = {
  content: ['components/*/*.dj', 'templates/**/*.html'],
  theme: { extend: {} },
  plugins: []
};
''')

    # Write Jest config
    with open('jest.config.ts', 'w') as f:
        f.write('''import type { Config } from 'jest';

const config: Config = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  moduleFileExtensions: ['ts', 'js'],
  transform: {
    '^.+\\.ts$': 'ts-jest'
  }
};

export default config;
''')

    # Write ESLint config
    with open('.eslintrc.js', 'w') as f:
        f.write('''module.exports = {
  env: {
    browser: true,
    es2021: true
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  plugins: ['@typescript-eslint'],
  rules: {}
};
''')

    # Write Vite plugin
    with open('djuno/vite/plugin-djuno.ts', 'w') as f:
        f.write('''import { Plugin } from 'vite';

export default function djunoPlugin(): Plugin {
  return {
    name: 'vite-plugin-djuno',
    transform(src, id) {
      if (id.endsWith('.dj')) {
        const templateMatch = src.match(/<template>(.*?)</template>/s);
        const styleMatch = src.match(/<style scoped>(.*?)</style>/s);
        const scriptMatch = src.match(/<script lang="ts">(.*?)</script>/s);
        
        let code = 'export default {';
        if (templateMatch) {
          code += `template: \`${templateMatch[1].trim()}\`,`;
          const slots = templateMatch[1].match(/<slot\s*(name="([^"]+)")?\s*\/?>/g) || [];
          code += `slots: [${slots.map(s => {
            const nameMatch = s.match(/name="([^"]+)"/);
            return `"${nameMatch ? nameMatch[1] : 'default'}"`;
          }).join(', ')}],`;
        }
        if (styleMatch) {
          code += `css: \`${styleMatch[1].trim()}\`,`;
        }
        if (scriptMatch) {
          code += scriptMatch[1].trim();
        }
        code += '};';
        
        return {
          code,
          map: null
        };
      }
    }
  };
}
''')

    # Write button template
    with open('djuno/templates/button.dj', 'w') as f:
        f.write('''<template>
  <button
    class="{{ class }} {{ styles.default }}"
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
    @apply bg-gray-100 p-4 rounded transition flex items-center;
  }
  .default:hover {
    @apply bg-gray-200;
  }
  .disabled {
    @apply opacity-50 cursor-not-allowed;
  }
</style>

<script lang="ts">
  /**
   * A customizable button component with named slots, icons, Alpine.js, and HTMX.
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

    # Write icon template
    with open('djuno/templates/icon.dj', 'w') as f:
        f.write('''<template>
  <span
    class="{{ class }} {{ styles.default }}"
    {% if id %}id="{{ id }}"{% endif %}
  >
    <svg class="w-5 h-5" fill="currentColor">
      <use xlink:href="/static/icons.svg#{{ name }}"></use>
    </svg>
  </span>
</template>

<style scoped>
  .default {
    @apply inline-block;
  }
</style>

<script lang="ts">
  /**
   * An icon component for displaying SVG icons.
   * @example <icon_component name="star" />
   */
  export default {
    name: '{{ name }}',
    props: {
      id: { type: String as () => string | null, default: null },
      name: { type: String as () => string, required: true },
      class: { type: String as () => string, default: 'default' }
    }
  };
</script>
''')

    # Write base template
    with open('templates/base.html', 'w') as f:
        f.write('''{% load djuno %}
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="{% static 'vite/button_default_abc123.css' %}">
  <link rel="stylesheet" href="{% static 'vite/icon_default_abc123.css' %}">
  <script src="https://unpkg.com/alpinejs" defer></script>
</head>
<body>
  {% block content %}{% endblock %}
</body>
</html>
''')

    # Write static icons.svg
    with open('static/icons.svg', 'w') as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <symbol id="star" viewBox="0 0 24 24">
    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
  </symbol>
</svg>
''')

    click.echo("Djuno initialized! Run `djuno dev` for development.")


@cli.command()
@click.argument('name')
@click.option('--template', default='button', help='Template to use')
@click.option('--js', default='none', type=click.Choice(['none', 'alpine', 'htmx']), prompt='JavaScript framework?')
def add(name, template, js):
    """Generate a new component."""
    component_dir = Path('components') / name
    component_dir.mkdir(exist_ok=True)
    dj_file = component_dir / f"{name}.dj"
    story_file = component_dir / f"{name}.stories.ts"
    test_file = component_dir / f"{name}.test.ts"

    # Load template
    template_path = Path('djuno/templates') / f'{template}.dj'
    if not template_path.exists():
        click.echo(f"Template '{template}' not found!")
        return
    with open(template_path) as f:
        content = f.read()

    # Write .dj file
    with open(dj_file, 'w') as f:
        f.write(content.replace('{{ name }}', name))

    # Write Storybook story
    template_name = template.split('/')[-1].replace('.dj', '')
    story_content = f'''import type {{ Meta, StoryObj }} from '@storybook/html';
import {{ renderDjango }} from '@storybook/django';

/**
 * {name.capitalize()} component.
 */
const meta: Meta = {{
  title: 'Components/{name.capitalize()}',
  argTypes: {{'''
    if template_name == 'button':
        story_content += '''
    id: { control: 'text', description: 'Unique identifier' },
    text: { control: 'text', description: 'Button text' },
    class: { control: 'text', description: 'CSS class' },
    js: { control: 'select', options: ['none', 'alpine', 'htmx'], description: 'JS framework' },
    disabled: { control: 'boolean', description: 'Disable button' },
    icon: { control: 'text', description: 'Icon component' },
    header: { control: 'text', description: 'Header slot content' },
    footer: { control: 'text', description: 'Footer slot content' }
  }},
  parameters: {{
    docs: {{
      description: {{
        component: 'A customizable button component with named slots and icon support.'
      }}
    }}
  }},
  render: (args) => renderDjango(`<button_component 
    text="${{args.text}}" 
    class="${{args.class}}" 
    js="${{args.js}}" 
    ${{args.id ? `id="${{args.id}}"` : ''}} 
    ${{args.disabled ? 'disabled="true"' : ''}}
    ${{args.icon ? `icon="${{args.icon}}"` : ''}}
  >${{args.header ? `<template slot="header">${{args.header}}</template>` : ''}}${{args.slot || ''}}${{args.footer ? `<template slot="footer">${{args.footer}}</template>` : ''}}</button_component>`, args)
}};

export default meta;
type Story = StoryObj;

export const Default: Story = {{
  args: {{
    text: 'Click Me',
    class: 'default',
    js: '{js}',
    disabled: false
  }}
}};

export const Disabled: Story = {{
  args: {{
    text: 'Disabled Button',
    class: 'default',
    disabled: true
  }}
}};

export const WithIcon: Story = {{
  args: {{
    text: 'Button with Icon',
    icon: '<icon_component name="star" />'
  }}
}};

export const WithNamedSlots: Story = {{
  args: {{
    text: 'Slotted Button',
    header: '<icon_component name="star" />',
    footer: '<span>Footer</span>'
  }}
}};
'''
    else:
        story_content += '''
    id: { control: 'text', description: 'Unique identifier' },
    name: { control: 'text', description: 'Icon name' },
    class: { control: 'text', description: 'CSS class' }
  }},
  parameters: {{
    docs: {{
      description: {{
        component: 'An icon component for displaying SVG icons.'
      }}
    }}
  }},
  render: (args) => renderDjango(`<icon_component 
    name="${{args.name}}" 
    class="${{args.class}}" 
    ${{args.id ? `id="${{args.id}}"` : ''}}
  />`, args)
}};

export default meta;
type Story = StoryObj;

export const Default: Story = {{
  args: {{
    name: 'star',
    class: 'default'
  }}
}};
'''

    with open(story_file, 'w') as f:
        f.write(story_content)

    # Write Jest test
    test_content = f'''import {{ render, screen }} from '@testing-library/djuno';
import {name} from './{name}.dj';

describe('{name} Component', () => {{'''
    if template_name == 'button':
        test_content += '''
  test('renders with correct text', () => {
    const { container } = render('<button_component text="Test Button" />');
    expect(screen.getByText('Test Button')).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });

  test('applies disabled attribute', () => {
    render('<button_component text="Disabled" disabled="true" />');
    expect(screen.getByText('Disabled')).toHaveAttribute('disabled');
  });

  test('renders icon', () => {
    render('<button_component text="With Icon" icon="<icon_component name=\\"star\\" />" />');
    expect(screen.getByText('With Icon').querySelector('svg')).toBeInTheDocument();
  });

  test('renders named slots', () => {
    render('<button_component text="Default"><template slot="header"><span>Header</span></template><template slot="footer"><span>Footer</span></template></button_component>');
    expect(screen.getByText('Header')).toBeInTheDocument();
    expect(screen.getByText('Footer')).toBeInTheDocument();
  });
'''
    else:
        test_content += '''
  test('renders with correct icon', () => {
    const { container } = render('<icon_component name="star" />');
    expect(container.querySelector('svg')).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });
'''

    test_content += '});'
    with open(test_file, 'w') as f:
        f.write(test_content)

    click.echo(f"Component '{name}' created at {component_dir}")


@cli.command()
def dev():
    """Run development servers (Vite, Django, Storybook)."""
    with ProcessPoolExecutor() as executor:
        executor.submit(subprocess.run, ['npm', 'run', 'dev'])
        executor.submit(subprocess.run, ['python', 'manage.py', 'runserver'])
        executor.submit(subprocess.run, ['npm', 'run', 'storybook'])


@cli.command()
def storybook():
    """Run Storybook for component previews."""
    subprocess.run(['npm', 'run', 'storybook'])


@cli.command()
def test():
    """Run Jest and Django tests."""
    subprocess.run(['npm', 'run', 'test'])
    subprocess.run(['python', 'manage.py', 'test'])


@cli.command()
def lint():
    """Lint and auto-fix component files."""
    subprocess.run(['npm', 'run', 'lint'])
    subprocess.run(['mypy', 'djuno', 'components', 'tests'])


@cli.command()
@click.argument('names', nargs=-1)
@click.option('--template', default='button', help='Template to use')
@click.option('--js', default='none', type=click.Choice(['none', 'alpine', 'htmx']))
def generate(names, template, js):
    """Generate multiple components."""
    for name in names:
        subprocess.run(
            ['djuno', 'add', name, '--template', template, '--js', js])
    click.echo(f"Generated components: {', '.join(names)}")


@cli.command()
def deploy():
    """Optimize and deploy for production."""
    subprocess.run(['npm', 'run', 'build'])
    subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])
    click.echo("Production build complete.")


if __name__ == '__main__':
    cli()
