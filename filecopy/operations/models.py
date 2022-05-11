import time
from enum import Enum
from enum import unique
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Set
from typing import Union


def get_timestamp() -> int:
    """Return current timestamp."""

    return round(time.time())


def append_suffix_to_filepath(filepath: Union[Path, str], suffix: Union[str, int], separator: str = '_') -> str:
    """Append suffix to filepath before extension."""

    path = Path(filepath)

    current_extension = ''.join(path.suffixes)
    new_extension = f'{separator}{suffix}{current_extension}'

    filename_parts = [path.name, '']
    if current_extension:
        filename_parts = path.name.rsplit(current_extension, 1)

    filename = new_extension.join(filename_parts)

    filepath = str(path.parent / filename)

    return filepath


@unique
class ResourceType(str, Enum):
    """Store all possible types of resources."""

    FOLDER = 'folder'
    FILE = 'file'
    CONTAINER = 'Container'


@unique
class ZoneType(str, Enum):
    GREENROOM = 0
    CORE = 1


class Node(dict):
    """Store information about one node."""

    def __str__(self) -> str:
        return f'{self.id} | {self.name}'

    def __dict__(self) -> dict:
        return self

    @property
    def parent(self) -> str:
        return self['parent']

    @property
    def parent_path(self) -> str:
        return self['parent_path']

    @property
    def id(self) -> str:
        return self['id']

    @property
    def is_folder(self) -> bool:
        return ResourceType.FOLDER == self['type']

    @property
    def is_file(self) -> bool:
        return ResourceType.FILE == self['type']

    @property
    def is_archived(self) -> bool:
        return self['archived'] is True

    @property
    def name(self) -> str:
        return self['name']

    @property
    def tags(self) -> List[str]:
        return self.get('tags', [])

    @property
    def display_path(self) -> Path:
        full_path = '{}/{}'.format(self['parent_path'].replace('.', '/'), self['name'])
        display_path = Path(full_path)

        if display_path.is_absolute():
            display_path = display_path.relative_to('/')

        return display_path

    def get_attributes(self) -> Dict[str, Any]:
        return self['extended']['extra'].get('attributes', {})


class NodeList(list):
    """Store list of Nodes."""

    def __init__(self, nodes: List[Dict[str, Any]]) -> None:
        super().__init__([Node(node) for node in nodes])

    @property
    def ids(self) -> Set[str]:
        return {node.id for node in self}

    def filter_files(self) -> 'NodeList':
        return NodeList([node for node in self if node.is_file])
