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

from enum import Enum
from typing import Optional
from typing import Set
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.engine import CursorResult


class EntityType(str, Enum):
    FOLDER = 'folder'
    FILE = 'file'


class ReviewStatus(str, Enum):
    DENIED = 'denied'
    PENDING = 'pending'
    APPROVED = 'approved'


class CopyStatus(str, Enum):
    PENDING = 'pending'
    COPIED = 'copied'


class ApprovalEntity(BaseModel):
    """Model to represent one approval entity."""

    id: UUID
    request_id: Optional[UUID]
    entity_id: Optional[str]
    entity_type: Optional[EntityType]
    review_status: Optional[ReviewStatus]
    parent_id: Optional[str]
    copy_status: Optional[CopyStatus]
    name: str

    class Config:
        orm_mode = True

    @property
    def is_approved_for_copy(self) -> bool:
        return (
            self.entity_type == EntityType.FILE
            and self.review_status == ReviewStatus.APPROVED
            and self.copy_status == CopyStatus.PENDING
        )


class ApprovalRequest(BaseModel):
    """Model to represent one approval request."""

    id: UUID
    destination_id: str
    source_id: str
    destination_path: str
    source_path: str

    class Config:
        orm_mode = True


class ApprovedApprovalEntities(dict):
    """Store approved approval entities using entity geid as a key.

    May include folder entities if those are parents for the approved file entity.
    """

    @property
    def geids(self) -> Set[str]:
        """Return all geids for all entities."""

        return set(self.keys())


class ApprovalEntities(dict):
    """Store multiple approval entities from one request using entity geid as a key."""

    @classmethod
    def from_cursor(cls, result: CursorResult):
        """Load approval entities from sqlalchemy cursor result."""

        instance = cls()
        for entity in result:
            approval_entity = ApprovalEntity.from_orm(entity)
            instance[approval_entity.entity_id] = approval_entity

        return instance

    def get_approved_entities_until_top_parent(self, approval_entity: ApprovalEntity) -> ApprovedApprovalEntities:
        """Return approval entity and all parent folder entities."""

        approved_entities = ApprovedApprovalEntities()
        approved_entities[approval_entity.entity_id] = approval_entity

        current = approval_entity
        while current.parent_id:
            current = self[current.parent_id]
            approved_entities[current.entity_id] = current

        return approved_entities

    def get_approved(self) -> ApprovedApprovalEntities:
        """Return approved entities with pending copy status.

        Also includes folder entities if those are parents for the file entity.
        """

        approved_entities = ApprovedApprovalEntities()

        for _, entity in self.items():
            if entity.is_approved_for_copy:
                approved_entities.update(self.get_approved_entities_until_top_parent(entity))

        return approved_entities
