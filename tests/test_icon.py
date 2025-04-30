from django.test import TestCase
from djuno.registry import registry


class IconComponentTest(TestCase):
    def test_icon_render(self):
        icon = registry['icon'](name="star")
        html = icon.render()
        self.assertIn('svg', html)
        self.assertIn('star', html)

    def test_required_prop(self):
        with self.assertRaises(ValueError):
            registry['icon']()
