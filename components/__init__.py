from django.apps import apps
import os


def register_all_components():
    for app_config in apps.get_app_configs():
        components_dir = os.path.join(app_config.path, 'components')
        if os.path.exists(components_dir):
            for component_dir in os.listdir(components_dir):
                component_path = os.path.join(
                    components_dir, component_dir, f"{component_dir}.py")
                if os.path.exists(component_path):
                    module_name = f"{app_config.name}.components.{
                        component_dir}.{component_dir}"
                    __import__(module_name)


register_all_components()
