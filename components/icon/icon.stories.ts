import type { Meta, StoryObj } from '@storybook/html';
import { renderDjango } from '@storybook/django';

const meta: Meta = {
  title: 'Components/Icon',
  argTypes: {
    id: { control: 'text', description: 'Unique identifier' },
    name: { control: 'text', description: 'Icon name' },
    class: { control: 'text', description: 'CSS class' }
  },
  parameters: {
    docs: {
      description: {
        component: 'An icon component for displaying SVG icons.'
      }
    }
  },
  render: (args) => renderDjango(`<icon_component 
    name="${args.name}" 
    class="${args.class}" 
    ${args.id ? `id="${args.id}"` : ''}
  />`, args)
};

export default meta;
type Story = StoryObj;

export const Default: Story = {
  args: {
    name: 'star',
    class: 'default'
  }
};
