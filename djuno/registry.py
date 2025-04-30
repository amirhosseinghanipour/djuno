from typing import Dict, Type
from .component import Component, from_dj_file
from glob import glob
from pathlib import Path
import watchfiles
import os


class ComponentRegistry:
    def __init__(self, base_dir: str):
        self.components: Dict[str, Type[Component]] = {}
        self.base_dir = base_dir
        self.file_paths: Dict[str, str] = {}
        self.load_component_paths()

        if os.getenv('DJUNO_ENV') == 'development':
            for changes in watchfiles.watch(base_dir):
                self.load_component_paths()

    def load_component_paths(self):
        self.file_paths.clear()
        for dj_file in glob(f'{self.base_dir}/*/*.dj'):
            name = Path(dj_file).stem
            self.file_paths[name] = dj_file

    def __getitem__(self, key: str) -> Type[Component]:
        if key not in self.components:
            self.components[key] = from_dj_file(self.file_paths[key])
        return self.components[key]


registry = ComponentRegistry('components')
