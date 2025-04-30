from django.test import TestCase
from djuno.registry import registry


class ButtonComponentTest(TestCase):
    def test_button_render(self):
        button = registry['button'](text="Test Button", class="default")
        html = button.render()
        self.assertIn('Test Button', html)
        self.assertIn('bg-gray-100', html)

    def test_required_prop(self):
        with self.assertRaises(ValueError):
            registry['button']()

    def test_invalid_choice(self):
        with self.assertRaises(ValueError):
            registry['button'](text="Test", js="invalid")

    def test_hydration(self):
        button = registry['button'](text="Test", js="alpine")
        html = button.render()
        self.assertIn('Alpine.hydrate', html)

    def test_slot_content(self):
        button = registry['button'](text="Default", slots={
                                    'default': '<span>Custom</span>'})
        html = button.render()
        self.assertIn('Custom', html)

    def test_named_slots(self):
        button = registry['button'](text="Default", slots={
            'header': '<span>Header</span>',
            'footer': '<span>Footer</span>'
        })
        html = button.render()
        self.assertIn('Header', html)
        self.assertIn('Footer', html)

    def test_icon_nesting(self):
        icon = registry['icon'](name="star").render()
        button = registry['button'](text="With Icon", icon=icon)
        html = button.render()
        self.assertIn('svg', html)
