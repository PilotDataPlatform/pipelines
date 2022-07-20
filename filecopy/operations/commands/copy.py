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

import asyncio
import atexit
import uuid
from pathlib import Path
from typing import Optional
from typing import Set

import click
from common import ProjectClient
from operations.config import get_settings
from operations.kafka_producer import KafkaProducer
from operations.managers import CopyManager
from operations.managers import CopyPreparationManager
from operations.minio_boto3_client import MinioBoto3Client
from operations.services.approval.client import ApprovalServiceClient
from operations.services.audit_trail.client import AuditTrailServiceClient
from operations.services.dataops.client import DataopsServiceClient
from operations.services.dataops.client import JobStatus
from operations.services.dataops.client import ResourceLockOperation
from operations.services.lineage.client import LineageServiceClient
from operations.services.metadata.client import MetadataServiceClient
from operations.traverser import Traverser
from sqlalchemy import MetaData
from sqlalchemy import create_engine

atexit.register(KafkaProducer.close_connection)


@atexit.register
@click.command()
@click.option('--source-id', type=str, required=True)
@click.option('--destination-id', type=str, required=True)
@click.option('--include-ids', type=str, multiple=True)
@click.option('--job-id', type=str, required=True)
@click.option('--session-id', type=str, required=True)
@click.option('--project-code', type=str, required=True)
@click.option('--operator', type=str, required=True)
@click.option('--request-id', type=click.UUID)
def copy(
    source_id: str,
    destination_id: str,
    include_ids: Optional[Set[str]],
    job_id: str,
    session_id: str,
    project_code: str,
    operator: str,
    request_id: Optional[uuid.UUID],
):
    """Copy files from source geid into destination geid."""

    click.echo(
        f'Starting copy process from "{source_id}" into "{destination_id}" \
        including only "{set(include_ids)}".'
    )

    settings = get_settings()

    project_client = ProjectClient(settings.PROJECT_SERVICE, settings.REDIS_URL)

    metadata_service_client = MetadataServiceClient(
        settings.METADATA_SERVICE, settings.S3_URL, settings.CORE_ZONE_LABEL, settings.TEMP_DIR, project_client
    )
    dataops_client = DataopsServiceClient(settings.DATAOPS_SERVICE)
    audit_trail_service_client = AuditTrailServiceClient(settings.AUDIT_TRAIL_SERVICE)
    lineage_service_client = LineageServiceClient(settings.LINEAGE_SERVICE)

    minio_client = MinioBoto3Client(
        settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY, settings.S3_URL, settings.S3_INTERNAL_HTTPS
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(KafkaProducer.init_connection())

    approval_service_client = None
    approved_entities = None

    try:
        if request_id:
            approval_service_client = ApprovalServiceClient(
                engine=create_engine(url=settings.DB_URI, future=True),
                metadata=MetaData(schema=settings.RDS_SCHEMA),
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
            set(include_ids[0].split(',')),
        )
        traverser = Traverser(copy_preparation_manager)
        traverser.traverse_tree(source_folder, destination_folder.display_path)

        loop = asyncio.get_event_loop()
        project = loop.run_until_complete(metadata_service_client.get_project_by_code(project_code))

        try:
            dataops_client.lock_resources(copy_preparation_manager.read_lock_paths, ResourceLockOperation.READ)
            dataops_client.lock_resources(copy_preparation_manager.write_lock_paths, ResourceLockOperation.WRITE)

            pipeline_name = 'data_transfer_folder'
            pipeline_desc = 'the script will copy the folder \
                from greenroom to core recursively'
            operation_type = 'copy'

            system_tags = [settings.COPIED_WITH_APPROVAL_TAG]
            copy_manager = CopyManager(
                metadata_service_client,
                lineage_service_client,
                audit_trail_service_client,
                dataops_client,
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
                set(include_ids[0].split(',')),
            )
            traverser = Traverser(copy_manager)
            traverser.traverse_tree(source_folder, destination_folder)
        finally:
            dataops_client.unlock_resources(copy_preparation_manager.read_lock_paths, ResourceLockOperation.READ)
            dataops_client.unlock_resources(copy_preparation_manager.write_lock_paths, ResourceLockOperation.WRITE)

        dataops_client.update_job(session_id, job_id, JobStatus.SUCCEED)
        click.echo('Copy operation has been finished successfully.')
    except Exception as e:
        click.echo(f'Exception occurred while performing copy operation:{e}')
        try:
            dataops_client.update_job(session_id, job_id, JobStatus.TERMINATED)
        except Exception as e:
            click.echo(f'Update job error: {e}')
