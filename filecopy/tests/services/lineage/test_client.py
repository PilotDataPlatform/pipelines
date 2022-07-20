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


class TestLineageServiceClient:
    def test_create_catalog_entity_returns_geid(self, lineage_service_client, httpserver, fake, create_node):
        expected_guid = fake.geid()
        body = {
            'result': {'mutatedEntities': {'CREATE': [{'guid': expected_guid}]}},
        }
        httpserver.expect_request('/v2/filedata').respond_with_json(body)
        node = create_node()

        received_geid = lineage_service_client.create_catalog_entity(node, fake.word(), fake.word())

        assert received_geid == expected_guid
