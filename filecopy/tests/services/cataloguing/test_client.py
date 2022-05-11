class TestCataloguingServiceClient:
    def test_create_catalog_entity_returns_geid(self, cataloguing_service_client, httpserver, fake, create_node):
        expected_guid = fake.geid()
        body = {
            'result': {'mutatedEntities': {'CREATE': [{'guid': expected_guid}]}},
        }
        httpserver.expect_request('/v2/filedata').respond_with_json(body)
        node = create_node()

        received_geid = cataloguing_service_client.create_catalog_entity(node, fake.word(), fake.word())

        assert received_geid == expected_guid
