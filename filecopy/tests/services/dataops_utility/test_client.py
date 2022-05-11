from pathlib import Path

from operations.services.dataops_utility.client import JobStatus
from operations.services.dataops_utility.client import ResourceLockOperation


class TestDataopsUtilityClient:
    def test_lock_resources_returns_response_body(self, dataops_utility_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v2/resource/lock/bulk').respond_with_json(expected_body)

        received_body = dataops_utility_client.lock_resources([Path('key')], ResourceLockOperation.READ)

        assert received_body == expected_body

    def test_unlock_resources_returns_response_body(self, dataops_utility_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v2/resource/lock/bulk').respond_with_json(expected_body, status=400)

        received_body = dataops_utility_client.unlock_resources([Path('key')], ResourceLockOperation.READ)

        assert received_body == expected_body

    def test_update_job_returns_response_body(self, dataops_utility_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/tasks/').respond_with_json(expected_body)

        received_body = dataops_utility_client.update_job(fake.geid(), fake.geid(), JobStatus.SUCCEED)

        assert received_body == expected_body

    def test_get_zip_preview_returns_response_body(self, dataops_utility_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/archive').respond_with_json(expected_body)

        received_body = dataops_utility_client.get_zip_preview(fake.geid())

        assert received_body == expected_body

    def test_get_zip_preview_returns_none_when_archive_does_not_exist(self, dataops_utility_client, httpserver, fake):
        httpserver.expect_request('/v1/archive').respond_with_json({}, status=404)

        received_body = dataops_utility_client.get_zip_preview(fake.geid())

        assert received_body is None

    def test_create_zip_preview_returns_response_body(self, dataops_utility_client, httpserver, fake):
        expected_body = fake.pydict(value_types=['str', 'int'])
        httpserver.expect_request('/v1/archive').respond_with_json(expected_body)

        received_body = dataops_utility_client.create_zip_preview(fake.geid(), fake.pydict(value_types=['str']))

        assert received_body == expected_body
