from operations.services.approval.models import ApprovalEntities


class TestApprovalServiceClient:
    def test_get_approval_entities_returns_instance_of_approval_entities(self, approval_service_client, fake):
        request_id = fake.uuid4()

        result = approval_service_client.get_approval_entities(request_id)

        assert isinstance(result, ApprovalEntities)
