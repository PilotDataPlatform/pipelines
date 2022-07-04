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
from pathlib import Path
from typing import List
from typing import Optional

import click
from common import ProjectClient
from operations.config import get_settings
from operations.kafka_producer import KafkaProducer
from operations.managers import DeleteManager
from operations.managers import DeletePreparationManager
from operations.minio_boto3_client import MinioBoto3Client
from operations.models import ZoneType
from operations.services.cataloguing.client import CataloguingServiceClient
from operations.services.dataops_utility.client import DataopsUtilityClient
from operations.services.dataops_utility.client import JobStatus
from operations.services.dataops_utility.client import ResourceLockOperation
from operations.services.metadata.client import MetadataServiceClient
from operations.services.provenance.client import ProvenanceServiceClient
from operations.traverser import Traverser


@click.command()
@click.option('--source-id', type=str, required=True)
@click.option('--include-ids', type=str, multiple=True)
@click.option('--job-id', type=str, required=True)
@click.option('--session-id', type=str, required=True)
@click.option('--project-code', type=str, required=True)
@click.option('--operator', type=str, required=True)
@click.option('--access-token', type=str, required=True)
def delete(
    source_id: str,
    include_ids: Optional[List[str]],
    job_id: str,
    session_id: str,
    project_code: str,
    operator: str,
    access_token: str,
):
    """Move files from source geid into trash bin."""

    click.echo(f'Starting delete process from "{source_id} including only "{set(include_ids)}".')

    settings = get_settings()
    project_client = ProjectClient(settings.PROJECT_SERVICE, settings.REDIS_URL)

    metadata_service_client = MetadataServiceClient(
        settings.METADATA_SERVICE, settings.MINIO_ENDPOINT, settings.CORE_ZONE_LABEL, settings.TEMP_DIR, project_client
    )
    dataops_utility_client = DataopsUtilityClient(settings.DATA_OPS_UTIL)
    provenance_service_client = ProvenanceServiceClient(settings.PROVENANCE_SERVICE)
    cataloguing_service_client = CataloguingServiceClient(settings.CATALOGUING_SERVICE)

    minio_client = MinioBoto3Client(access_token, settings.MINIO_ENDPOINT, settings.MINIO_HTTPS)

    kafka_client = KafkaProducer(settings.KAFKA_URL)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(kafka_client.init_connection())

    try:
        source_folder = metadata_service_client.get_item_by_id(source_id)
        destination_folder = Path()

        source_zone = settings.GREEN_ZONE_LABEL
        source_bucket = Path(f'gr-{project_code}')
        if source_folder['zone'] == ZoneType.CORE:
            source_zone = settings.CORE_ZONE_LABEL
            source_bucket = Path(f'core-{project_code}')

        delete_preparation_manager = DeletePreparationManager(
            metadata_service_client,
            project_code,
            source_zone,
            source_bucket,
            set(include_ids[0].split(',')),
        )
        traverser = Traverser(delete_preparation_manager)
        traverser.traverse_tree(source_folder, destination_folder)

        loop = asyncio.get_event_loop()
        project = loop.run_until_complete(metadata_service_client.get_project_by_code(project_code))

        try:
            dataops_utility_client.lock_resources(
                delete_preparation_manager.write_lock_paths, ResourceLockOperation.WRITE
            )

            pipeline_name = 'data_delete_folder'
            pipeline_desc = 'the script will delete the folder in \
                greenroom/core recursively'
            operation_type = 'delete'

            delete_manager = DeleteManager(
                metadata_service_client,
                cataloguing_service_client,
                provenance_service_client,
                dataops_utility_client,
                project,
                operator,
                minio_client,
                settings.CORE_ZONE_LABEL,
                settings.GREEN_ZONE_LABEL,
                pipeline_name,
                pipeline_desc,
                operation_type,
                set(include_ids[0].split(',')),
                kafka_client,
            )

            delete_manager.archive_nodes()

        finally:
            dataops_utility_client.unlock_resources(
                delete_preparation_manager.write_lock_paths, ResourceLockOperation.WRITE
            )

        dataops_utility_client.update_job(session_id, job_id, JobStatus.SUCCEED)
        click.echo('Delete operation has been finished successfully.')
    except Exception as e:
        click.echo(
            f'An exception occurred while performing \
            delete operation: {e}'
        )
        try:
            dataops_utility_client.update_job(session_id, job_id, JobStatus.TERMINATED)
        except Exception as e:
            click.echo(f'Update job error: {e}')
