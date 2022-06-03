# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

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
