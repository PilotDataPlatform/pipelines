import pytest
from operations.managers import NodeManager
from operations.models import Node
from operations.models import NodeList
from operations.models import ResourceType


@pytest.fixture
def node_manager(metadata_service_client) -> NodeManager:
    yield NodeManager(metadata_service_client)


class TestNodeManager:
    def test_get_tree_returns_node_list_with_parent_folder_geid(self, node_manager, httpserver, create_node, fake):
        parent_node = create_node(type_=ResourceType.FOLDER, name='folder1', id_='parent_id')
        parent_id = parent_node['id']
        response = {'result': parent_node}
        httpserver.expect_request(f'/v1/item/{parent_id}').respond_with_json(response)

        expected_node = create_node(type_=ResourceType.FOLDER, parent=parent_node['id'])
        body = {'results': [expected_node]}
        httpserver.expect_request('/v1/items/search/').respond_with_json(body)
        received_nodes = node_manager.get_tree(Node(parent_node))

        assert received_nodes == [expected_node]

    def test_exclude_nodes_returns_empty_set(self, node_manager, create_node):
        expected_set = set()
        received_set = node_manager.exclude_nodes(create_node(), NodeList([]))

        assert received_set == expected_set
