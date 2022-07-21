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

import random
from typing import Callable

import pytest
from operations.services.approval.models import ApprovalEntities
from operations.services.approval.models import ApprovalEntity
from operations.services.approval.models import ApprovedApprovalEntities
from operations.services.approval.models import CopyStatus
from operations.services.approval.models import EntityType
from operations.services.approval.models import ReviewStatus


@pytest.fixture
def create_approval_entity(fake) -> Callable[..., ApprovalEntity]:
    def _create_approval_entity(
        id_=None,
        request_id=None,
        entity_id=None,
        entity_type=None,
        review_status=...,
        parent_id=...,
        copy_status=...,
        name=None,
    ) -> ApprovalEntity:
        if id_ is None:
            id_ = fake.uuid4()

        if request_id is None:
            request_id = fake.uuid4()

        if entity_id is None:
            entity_id = fake.uuid4()

        if entity_type is None:
            entity_type = random.choice(list(EntityType))

        if review_status is ...:
            review_status = random.choice(list(ReviewStatus))

        if parent_id is ...:
            parent_id = fake.uuid4()

        if copy_status is ...:
            copy_status = random.choice(list(CopyStatus))

        if name is None:
            name = fake.word()

        return ApprovalEntity(
            id=id_,
            request_id=request_id,
            entity_id=entity_id,
            entity_type=entity_type,
            review_status=review_status,
            parent_id=parent_id,
            copy_status=copy_status,
            name=name,
        )

    return _create_approval_entity


class TestApprovalEntity:
    def test_model_creates_successfully(self, fake):
        ApprovalEntity(
            id=fake.uuid4(),
            request_id=fake.uuid4(),
            entity_id=fake.uuid4(),
            entity_type=random.choice(list(EntityType)),
            review_status=random.choice(list(ReviewStatus)),
            parent_id=fake.uuid4(),
            copy_status=random.choice(list(CopyStatus)),
            name=fake.word(),
        )


class TestApprovedApprovalEntities:
    def test_geids_property_returns_set_of_keys(self, fake, create_approval_entity):
        key1 = fake.geid()
        key2 = fake.geid()
        approved_entities = ApprovedApprovalEntities(
            {
                key1: create_approval_entity(),
                key2: create_approval_entity(),
            }
        )
        expected_geids = {key1, key2}

        assert approved_entities.geids == expected_geids


class TestApprovalEntities:
    def test_get_approved_entities_until_top_parent_returns_approval_entity_and_all_parent_folder_entities(
        self, create_approval_entity
    ):
        approval_entity_1 = create_approval_entity(parent_id=None, entity_type=EntityType.FOLDER)
        approval_entity_2 = create_approval_entity(parent_id=approval_entity_1.entity_id, entity_type=EntityType.FILE)

        approval_entities = ApprovalEntities(
            {
                approval_entity_1.entity_id: approval_entity_1,
                approval_entity_2.entity_id: approval_entity_2,
            }
        )

        expected_approved_entities = ApprovedApprovalEntities(
            {
                approval_entity_1.entity_id: approval_entity_1,
                approval_entity_2.entity_id: approval_entity_2,
            }
        )

        approved_entities = approval_entities.get_approved_entities_until_top_parent(approval_entity_2)

        assert approved_entities == expected_approved_entities

    def test_get_approved_returns_approved_entities_with_pending_copy_status(self, create_approval_entity):
        approval_entity_1 = create_approval_entity(
            parent_id=None,
            entity_type=EntityType.FILE,
            review_status=ReviewStatus.PENDING,
            copy_status=CopyStatus.PENDING,
        )
        approval_entity_2 = create_approval_entity(
            parent_id=None,
            entity_type=EntityType.FILE,
            review_status=ReviewStatus.APPROVED,
            copy_status=CopyStatus.PENDING,
        )

        approval_entities = ApprovalEntities(
            {
                approval_entity_1.entity_id: approval_entity_1,
                approval_entity_2.entity_id: approval_entity_2,
            }
        )

        expected_approved_entities = ApprovedApprovalEntities(
            {
                approval_entity_2.entity_id: approval_entity_2,
            }
        )

        approved_entities = approval_entities.get_approved()

        assert approved_entities == expected_approved_entities
