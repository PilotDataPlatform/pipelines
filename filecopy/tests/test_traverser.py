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

from operations.managers import NodeManager
from operations.models import Node
from operations.models import NodeList
from operations.models import ResourceType
from operations.traverser import Traverser


class TestTraverser:
    def test_traverse_tree_works_with_one_level_of_nesting(self, metadata_service_client, create_node):
        tree_nodes = NodeList([create_node(type_=ResourceType.FILE), create_node(type_=ResourceType.FILE)])

        class Manager(NodeManager):
            def get_tree(self, source_folder: Node):
                return tree_nodes.copy()

            def process_file(self, source_file: Node, destination_folder: Node):
                expected_node = tree_nodes.pop(0)
                assert expected_node == source_file

            def process_folder(self, source_folder: Node, destination_parent_folder: Node):
                pass

        traverser = Traverser(Manager(metadata_service_client))

        traverser.traverse_tree(create_node(), create_node())

        assert len(tree_nodes) == 0
