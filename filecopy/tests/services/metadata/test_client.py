# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General
# Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

class TestMetadataServiceClient:
    def test_is_file_exists_returns_true_if_node_exists(self, metadata_service_client, mocker, create_node):
        mocker.patch.object(metadata_service_client, 'get_node', return_value=create_node())

        received_response = metadata_service_client.is_file_exists('zone', 'code', 'path')

        assert received_response is True

    def test_is_file_exists_returns_false_if_node_does_not_exist(self, metadata_service_client, mocker):
        mocker.patch.object(metadata_service_client, 'get_node', return_value=None)

        received_response = metadata_service_client.is_file_exists('zone', 'code', 'path')

        assert received_response is False

    def test_is_folder_exists_returns_true_if_node_exists(self, metadata_service_client, mocker, create_node):
        mocker.patch.object(metadata_service_client, 'get_node', return_value=create_node())

        received_response = metadata_service_client.is_folder_exists('zone', 'code', 'path')

        assert received_response is True

    def test_is_folder_exists_returns_false_if_node_does_not_exist(self, metadata_service_client, mocker):
        mocker.patch.object(metadata_service_client, 'get_node', return_value=None)

        received_response = metadata_service_client.is_folder_exists('zone', 'code', 'path')

        assert received_response is False
