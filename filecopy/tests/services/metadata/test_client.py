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
