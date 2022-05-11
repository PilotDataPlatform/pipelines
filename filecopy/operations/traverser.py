from pathlib import Path
from typing import Union

from operations.managers import NodeManager
from operations.models import Node
from operations.models import NodeList


class Traverser:
    """Traverse the trees using node manipulations from node manager."""

    def __init__(self, node_manager: NodeManager) -> None:
        self.node_manager = node_manager

    def _traverse_tree(self, nodes: NodeList, source_folder: Node, destination_folder: Union[Path, Node]) -> None:
        excluded_geids = self.node_manager.exclude_nodes(source_folder, nodes)

        errors = []

        for source_entry in nodes:
            if source_entry.id in excluded_geids:
                continue

            try:
                if source_entry.is_folder:
                    existing_destination_folder = self.node_manager.process_folder(source_entry, destination_folder)
                    self.traverse_tree(source_entry, existing_destination_folder)
                else:
                    self.node_manager.process_file(source_entry, destination_folder)
            except Exception as e:
                errors.append(e)

        if errors:
            raise Exception(errors)

    def traverse_tree(self, source_folder: Node, destination_folder: Union[Path, Node]) -> None:
        """Start tree traversing."""

        nodes = self.node_manager.get_tree(source_folder)
        self._traverse_tree(nodes, source_folder, destination_folder)
