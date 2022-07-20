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

from pathlib import Path

from operations.services.dataops.client import JobStatus
from operations.services.dataops.client import ResourceLockOperation


class TestDataopsServiceClient:
    def test_lock_resources_returns_response_body(self, dataops_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v2/resource/lock/bulk').respond_with_json(expected_body)

        received_body = dataops_client.lock_resources([Path('key')], ResourceLockOperation.READ)

        assert received_body == expected_body

    def test_unlock_resources_returns_response_body(self, dataops_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v2/resource/lock/bulk').respond_with_json(expected_body, status=400)

        received_body = dataops_client.unlock_resources([Path('key')], ResourceLockOperation.READ)

        assert received_body == expected_body

    def test_update_job_returns_response_body(self, dataops_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/tasks/').respond_with_json(expected_body)

        received_body = dataops_client.update_job(fake.geid(), fake.geid(), JobStatus.SUCCEED)

        assert received_body == expected_body

    def test_get_zip_preview_returns_response_body(self, dataops_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/archive').respond_with_json(expected_body)

        received_body = dataops_client.get_zip_preview(fake.geid())

        assert received_body == expected_body

    def test_get_zip_preview_returns_none_when_archive_does_not_exist(self, dataops_client, httpserver, fake):
        httpserver.expect_request('/v1/archive').respond_with_json({}, status=404)

        received_body = dataops_client.get_zip_preview(fake.geid())

        assert received_body is None

    def test_create_zip_preview_returns_response_body(self, dataops_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/archive').respond_with_json(expected_body)

        received_body = dataops_client.create_zip_preview(fake.geid(), fake.pydict(value_types=['str']))

        assert received_body == expected_body
