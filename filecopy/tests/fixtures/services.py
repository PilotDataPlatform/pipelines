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

from uuid import uuid4

import pytest
from operations.services.approval.client import ApprovalServiceClient
from operations.services.audit_trail.client import AuditTrailServiceClient
from operations.services.dataops_utility.client import DataopsUtilityClient
from operations.services.lineage.client import LineageServiceClient
from operations.services.metadata.client import MetadataServiceClient
from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.future import create_engine


@pytest.fixture
def inmemory_engine():
    yield create_engine('sqlite:///:memory:', future=True)


@pytest.fixture
def metadata(inmemory_engine):
    metadata = MetaData()
    Table(
        'approval_entity',
        metadata,
        Column('id', String(), unique=True, primary_key=True, default=uuid4),
        Column('request_id', String()),
        Column('entity_type', String()),
        Column('review_status', String()),
    )
    Table(
        'approval_request',
        metadata,
        Column('id', String(), unique=True, primary_key=True, default=uuid4),
        Column('destination_geid', String()),
        Column('source_geid', String()),
        Column('destination_path', String()),
        Column('source_path', String()),
    )
    metadata.create_all(inmemory_engine)

    with inmemory_engine.connect() as connection:
        with connection.begin():
            metadata.create_all(connection)

    yield metadata


@pytest.fixture
def approval_service_client(inmemory_engine, metadata) -> ApprovalServiceClient:
    yield ApprovalServiceClient(inmemory_engine, metadata)


@pytest.fixture
def cataloguing_service_client(httpserver) -> LineageServiceClient:
    yield LineageServiceClient(httpserver.url_for('/'))


@pytest.fixture
def dataops_utility_client(httpserver) -> DataopsUtilityClient:
    yield DataopsUtilityClient(httpserver.url_for('/'))


@pytest.fixture
def metadata_service_client(httpserver) -> MetadataServiceClient:
    yield MetadataServiceClient(
        httpserver.url_for('/'), 'minio-endpoint', 'core-zone', 'temp-dir', httpserver.url_for('/')
    )


@pytest.fixture
def provenance_service_client(httpserver) -> AuditTrailServiceClient:
    yield AuditTrailServiceClient(httpserver.url_for('/'))
