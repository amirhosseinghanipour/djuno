import type { Meta, StoryObj } from '@storybook/html';
import { renderDjango } from '@storybook/django';

const meta: Meta = {
  title: 'Components/Button',
  argTypes: {
    id: { control: 'text', description: 'Unique identifier' },
    text: { control: 'text', description: 'Button text' },
    class: { control: 'text', description: 'CSS class' },
    js: { control: 'select', options: ['none', 'alpine', 'htmx'], description: 'JS framework' },
    disabled: { control: 'boolean', description: 'Disable button' },
    icon: { control: 'text', description: 'Icon component' },
    header: { control: 'text', description: 'Header slot content' },
    footer: { control: 'text', description: 'Footer slot content' }
  },
  parameters: {
    docs: {
      description: {
        component: 'A customizable button component with named slots and icon support.'
      }
    }
  },
  render: (args) => renderDjango(`<button_component 
    text="${args.text}" 
    class="${args.class}" 
    js="${args.js}" 
    ${args.id ? `id="${args.id}"` : ''} 
    ${args.disabled ? 'disabled="true"' : ''} 
    ${args.icon ? `icon="${args.icon}"` : ''}
  >${args.header ? `<template slot="header">${args.header}</template>` : ''}${args.slot || ''}${args.footer ? `<template slot="footer">${args.footer}</template>` : ''}</button_component>`, args)
};

export default meta;
type Story = StoryObj;

export const Default: Story = {
  args: {
    text: 'Click Me',
    class: 'default',
    js: 'none',
    disabled: false
  }
};

export const Disabled: Story = {
  args: {
    text: 'Disabled Button',
    class: 'default',
    disabled: true
  }
};

export const WithIcon: Story = {
  args: {
    text: 'Button with Icon',
    icon: '<icon_component name="star" />'
  }
};

export const WithNamedSlots: Story = {
  args: {
    text: 'Slotted Button',
    header: '<icon_component name="star" />',
    footer: '<span>Footer</span>'
  }
};
