from lxml import etree
from typing import Dict
import pickle
import hashlib
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_dj_file(file_path: str, use_cache: bool = True) -> Dict[str, str]:
    cache_dir = Path('djuno/cache/components')
    file_hash = hashlib.md5(Path(file_path).read_bytes()).hexdigest()
    cache_file = cache_dir / f"{file_hash}.pkl"

    if use_cache and cache_file.exists():
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    with open(file_path, 'r') as f:
        content = f.read()

    logger.debug(f"Parsing {file_path}")

    parser = etree.HTMLParser()
    tree = etree.fromstring(f'<root>{content}</root>', parser)

    sections = {'template': '', 'style': '', 'script': ''}
    for elem in tree:
        tag = elem.tag
        if tag in sections:
            if tag == 'template':
                sections[tag] = etree.tostring(
                    elem, encoding='unicode').strip()[10:-11]
            else:
                sections[tag] = ''.join(elem.itertext()).strip()

    logger.debug(f"Parsed sections: {sections}")

    # Cache compiled sections
    with open(cache_file, 'wb') as f:
        pickle.dump(sections, f)

    return sections
