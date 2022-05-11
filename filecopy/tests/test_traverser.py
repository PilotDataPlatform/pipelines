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
