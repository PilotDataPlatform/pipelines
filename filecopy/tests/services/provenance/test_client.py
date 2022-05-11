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

class TestProvenanceServiceClient:
    def test_create_lineage_v3_returns_response_body(self, provenance_service_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/lineage/').respond_with_json(expected_body)

        received_body = provenance_service_client.create_lineage_v3(
            fake.geid(), fake.geid(), fake.word(), fake.word(), fake.word()
        )

        assert received_body == expected_body

    def test_update_file_operation_logs_returns_response_body(self, provenance_service_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/audit-logs').respond_with_json(expected_body)

        received_body = provenance_service_client.update_file_operation_logs(
            fake.file_path(depth=3), fake.file_path(depth=3), fake.word(), fake.word(), fake.word()
        )

        assert received_body == expected_body

    def test_deprecate_index_in_es_returns_response_body(self, provenance_service_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/entity/file').respond_with_json(expected_body)

        received_body = provenance_service_client.deprecate_index_in_es(fake.geid())

        assert received_body == expected_body

    def test_create_index_in_es_returns_response_body(self, provenance_service_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/entity/file').respond_with_json(expected_body)

        received_body = provenance_service_client.create_index_in_es(fake.pydict(value_types=['str']))

        assert received_body == expected_body
