import uuid
from pathlib import Path
from typing import List
from typing import Optional
from typing import Set

import click
from operations.config import get_settings
from operations.managers import CopyManager
from operations.managers import CopyPreparationManager
from operations.minio_client import MinioClient
from operations.services.approval.client import ApprovalServiceClient
from operations.services.cataloguing.client import CataloguingServiceClient
from operations.services.dataops_utility.client import DataopsUtilityClient
from operations.services.dataops_utility.client import JobStatus
from operations.services.dataops_utility.client import ResourceLockOperation
from operations.services.metadata.client import MetadataServiceClient
from operations.services.provenance.client import ProvenanceServiceClient
from operations.traverser import Traverser
from sqlalchemy import MetaData
from sqlalchemy import create_engine


@click.command()
@click.option('--source-id', type=str, required=True)
@click.option('--destination-id', type=str, required=True)
@click.option('--include-ids', type=List[str])
@click.option('--job-id', type=str, required=True)
@click.option('--session-id', type=str, required=True)
@click.option('--project-code', type=str, required=True)
@click.option('--operator', type=str, required=True)
@click.option('--access-token', type=str, required=True)
@click.option('--refresh-token', type=str, required=True)
@click.option('--request-id', type=click.UUID)
def copy(
    source_id: str,
    destination_id: str,
    include_ids: Optional[Set[str]],
    job_id: str,
    session_id: str,
    project_code: str,
    operator: str,
    access_token: str,
    refresh_token: str,
    request_id: Optional[uuid.UUID],
):
    """Copy files from source geid into destination geid."""

    click.echo(
        f'Starting copy process from "{source_id}" into "{destination_id}" \
        including only "{include_ids}".'
    )

    settings = get_settings()

    metadata_service_client = MetadataServiceClient(
        settings.METADATA_SERVICE,
        settings.MINIO_ENDPOINT,
        settings.CORE_ZONE_LABEL,
        settings.TEMP_DIR,
        settings.NEO4J_SERVICE,
    )
    dataops_utility_client = DataopsUtilityClient(settings.DATA_OPS_UTIL)
    provenance_service_client = ProvenanceServiceClient(settings.PROVENANCE_SERVICE)
    cataloguing_service_client = CataloguingServiceClient(settings.CATALOGUING_SERVICE)

    minio_client = MinioClient(
        access_token,
        refresh_token,
        settings.MINIO_HOST,
        settings.MINIO_ENDPOINT,
        settings.MINIO_HTTPS,
        settings.KEYCLOAK_MINIO_SECRET,
        settings.KEYCLOAK_ENDPOINT,
    )

    approval_service_client = None
    approved_entities = None

    try:
        if request_id:
            approval_service_client = ApprovalServiceClient(
                engine=create_engine(url=settings.RDS_DB_URI, future=True),
                metadata=MetaData(schema=settings.RDS_SCHEMA_DEFAULT),
            )
            request_approval_entities = approval_service_client.get_approval_entities(str(request_id))
            approved_entities = request_approval_entities.get_approved()

        nodes = metadata_service_client.get_items_by_ids([source_id, destination_id])
        source_folder = nodes[source_id]
        destination_folder = nodes[destination_id]

        if destination_folder.is_archived:
            raise ValueError('Destination is already in trash bin')

        source_bucket = Path(f'gr-{project_code}')
        destination_bucket = Path(f'core-{project_code}')

        copy_preparation_manager = CopyPreparationManager(
            metadata_service_client,
            approval_service_client,
            approved_entities,
            project_code,
            settings.GREEN_ZONE_LABEL,
            settings.CORE_ZONE_LABEL,
            source_bucket,
            destination_bucket,
            include_ids,
        )
        traverser = Traverser(copy_preparation_manager)
        traverser.traverse_tree(source_folder, destination_folder.display_path)

        project = metadata_service_client.get_project_by_code(project_code)

        try:
            dataops_utility_client.lock_resources(copy_preparation_manager.read_lock_paths, ResourceLockOperation.READ)
            dataops_utility_client.lock_resources(
                copy_preparation_manager.write_lock_paths, ResourceLockOperation.WRITE
            )

            minio_client.check_connection()

            pipeline_name = 'data_transfer_folder'
            pipeline_desc = 'the script will copy the folder \
                from greenroom to core recursively'
            operation_type = 'data_transfer'

            system_tags = [settings.COPIED_WITH_APPROVAL_TAG]
            copy_manager = CopyManager(
                metadata_service_client,
                cataloguing_service_client,
                provenance_service_client,
                dataops_utility_client,
                approval_service_client,
                approved_entities,
                copy_preparation_manager.duplicated_files,
                system_tags,
                project,
                operator,
                minio_client,
                settings.CORE_ZONE_LABEL,
                settings.GREEN_ZONE_LABEL,
                pipeline_name,
                pipeline_desc,
                operation_type,
                include_ids,
            )
            traverser = Traverser(copy_manager)
            traverser.traverse_tree(source_folder, destination_folder)
        finally:
            dataops_utility_client.unlock_resources(
                copy_preparation_manager.read_lock_paths, ResourceLockOperation.READ
            )
            dataops_utility_client.unlock_resources(
                copy_preparation_manager.write_lock_paths, ResourceLockOperation.WRITE
            )

        dataops_utility_client.update_job(session_id, job_id, JobStatus.SUCCEED)
        click.echo('Copy operation has been finished successfully.')
    except Exception as e:
        click.echo(f'Exception occurred while performing copy operation:{e}')
        try:
            dataops_utility_client.update_job(session_id, job_id, JobStatus.TERMINATED)
        except Exception as e:
            click.echo(f'Update job error: {e}')
