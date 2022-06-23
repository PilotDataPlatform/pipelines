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
        httpserver.expect_request(f'/v1/item/{parent_id}/').respond_with_json({'result': parent_node})

        expected_node = create_node(type_=ResourceType.FOLDER, parent=parent_node['id'])
        body = {'result': [expected_node]}
        httpserver.expect_request('/v1/items/search/').respond_with_json(body)
        received_nodes = node_manager.get_tree(Node(parent_node))

        assert received_nodes == [expected_node]

    def test_exclude_nodes_returns_empty_set(self, node_manager, create_node):
        expected_set = set()
        received_set = node_manager.exclude_nodes(create_node(), NodeList([]))

        assert received_set == expected_set
