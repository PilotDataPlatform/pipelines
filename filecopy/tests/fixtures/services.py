from uuid import uuid4

import pytest
from operations.services.approval.client import ApprovalServiceClient
from operations.services.cataloguing.client import CataloguingServiceClient
from operations.services.dataops_utility.client import DataopsUtilityClient
from operations.services.metadata.client import MetadataServiceClient
from operations.services.provenance.client import ProvenanceServiceClient
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
def cataloguing_service_client(httpserver) -> CataloguingServiceClient:
    yield CataloguingServiceClient(httpserver.url_for('/'))


@pytest.fixture
def dataops_utility_client(httpserver) -> DataopsUtilityClient:
    yield DataopsUtilityClient(httpserver.url_for('/'))


@pytest.fixture
def metadata_service_client(httpserver) -> MetadataServiceClient:
    yield MetadataServiceClient(
        httpserver.url_for('/'), 'minio-endpoint', 'core-zone', 'temp-dir', httpserver.url_for('/')
    )


@pytest.fixture
def provenance_service_client(httpserver) -> ProvenanceServiceClient:
    yield ProvenanceServiceClient(httpserver.url_for('/'))
