from pathlib import Path

import pytest
from operations.models import Node
from operations.models import NodeList
from operations.models import ResourceType
from operations.models import append_suffix_to_filepath


@pytest.mark.parametrize(
    'filepath,suffix,expected',
    [
        ('file.tar.gz', 'suffix', 'file_suffix.tar.gz'),
        ('/path/to/file.tar.gz', 'outdated', '/path/to/file_outdated.tar.gz'),
        ('folder.tar.gz/file.tar.gz', 'tar', 'folder.tar.gz/file_tar.tar.gz'),
        ('image.jpg', 1638552343, 'image_1638552343.jpg'),
        ('file', 'suffix', 'file_suffix'),
        (Path('path/to/file'), 'suffix', 'path/to/file_suffix'),
    ],
)
def test_append_suffix_to_filename_appends_suffix_as_expected(filepath, suffix, expected) -> None:
    assert append_suffix_to_filepath(filepath, suffix) == expected


class TestNode:
    def test_id_returns_node_id(self, create_node):
        node = create_node()
        expected_id = node['id']

        assert node.id == expected_id

    def test_is_folder_returns_true_if_labels_contain_folder_type(self, create_node):
        node = create_node(type_=ResourceType.FOLDER)

        assert node.is_folder is True

    def test_is_folder_returns_false_if_labels_does_not_contain_folder_type(self, create_node):
        node = create_node(type_=ResourceType.FILE)

        assert node.is_folder is False

    def test_is_file_returns_true_if_labels_contain_file_type(self, create_node):
        node = create_node(type_=ResourceType.FILE)

        assert node.is_file is True

    def test_is_file_returns_false_if_labels_does_not_contain_file_type(self, create_node):
        node = create_node(type_=ResourceType.FOLDER)

        assert node.is_file is False

    def test_is_archived_returns_true_if_archived_property_is_true(self, create_node):
        node = create_node(archived=True)

        assert node.is_archived is True

    def test_is_archived_returns_false_if_archived_property_is_false(self, create_node):
        node = create_node(archived=False)

        assert node.is_archived is False

    def test_id_returns_node_global_entity_id(self, create_node):
        node = create_node()
        expected_id = node['id']

        assert node.id == expected_id

    def test_name_returns_node_name(self, create_node):
        node = create_node()
        expected_name = node['name']

        assert node.name == expected_name

    def test_tags_returns_node_tags(self, create_node):
        node = create_node()
        expected_tags = node['extended']['extra']['tags']

        assert node.tags == expected_tags

    def test_get_attributes_returns_attributes_which_starts_with_attr(self, create_node):
        node = create_node(attributes={'attr_one': 1})
        expected_attributes = {'attr_one': 1}

        assert expected_attributes == node.get_attributes()


class TestNodeList:
    def test_new_instance_converts_list_values_into_node_instances(self):
        nodes = NodeList([{'key': 'value'}])

        assert isinstance(nodes[0], Node)

    def test_ids_returns_set_with_all_node_ids(self, create_node):
        node_1 = create_node()
        node_2 = create_node()
        nodes = NodeList([node_1, node_2])
        expected_ids = {node_1.id, node_2.id}

        assert expected_ids == nodes.ids

    def test_filter_files_returns_node_list_with_file_nodes_only(self, create_node):
        node_1 = create_node(type_=ResourceType.FILE)
        node_2 = create_node(type_=ResourceType.FOLDER)
        nodes = NodeList([node_1, node_2])
        expected_nodes = NodeList([node_1])

        assert expected_nodes == nodes.filter_files()
