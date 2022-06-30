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

import logging
from pathlib import Path
from typing import List
from typing import Optional
from typing import Set
from typing import Union

from operations.duplicated_file_names import DuplicatedFileNames
from operations.kafka_producer import KafkaProducer
from operations.minio_boto3_client import MinioBoto3Client
from operations.models import Node
from operations.models import NodeList
from operations.models import get_timestamp
from operations.services.approval.client import ApprovalServiceClient
from operations.services.approval.models import ApprovedApprovalEntities
from operations.services.approval.models import CopyStatus
from operations.services.cataloguing.client import CataloguingServiceClient
from operations.services.dataops_utility.client import DataopsUtilityClient
from operations.services.metadata.client import MetadataServiceClient
from operations.services.provenance.client import ProvenanceServiceClient

logger = logging.getLogger(__name__)


class NodeManager:
    """Base class for node manipulations that is used in the Traverser."""

    def __init__(self, metadata_service_client: MetadataServiceClient) -> None:
        self.metadata_service_client = metadata_service_client

    def get_tree(self, source_folder: Node) -> NodeList:
        """Return child nodes from current source folder."""
        nodes = self.metadata_service_client.get_nodes_tree(source_folder.id, False)
        return nodes

    def exclude_nodes(self, source_folder: Node, nodes: NodeList) -> Set[str]:
        """Return set of ids that should be excluded when copying from this source folder."""

        return set()

    def process_file(self, source_file: Node, destination_folder: Union[Path, Node]) -> None:
        """Process one file."""

        raise NotImplementedError

    def process_folder(self, source_folder: Node, destination_parent_folder: Union[Path, Node]) -> Union[Path, Node]:
        """Process one folder."""

        raise NotImplementedError


class BaseCopyManager(NodeManager):
    """Base manager for copying process with approved entities."""

    def __init__(
        self,
        metadata_service_client: MetadataServiceClient,
        approval_service_client: Optional[ApprovalServiceClient],
        approved_entities: Optional[ApprovedApprovalEntities],
        include_ids: Optional[Set[str]],
    ) -> None:
        super().__init__(metadata_service_client)

        self.approval_service_client = approval_service_client
        self.approved_entities = approved_entities
        self.include_ids = include_ids

    def _is_node_approved(self, node: Node) -> bool:
        """Check if node geid is in a list of approved entities.

        If approved entities are not set then node is considered approved.
        """

        if self.approved_entities is None:
            return True

        return node.id in self.approved_entities

    def _update_approval_entity_copy_status_for_node(self, node: Node, copy_status: CopyStatus) -> None:
        """Update copy status field for approval entity related to node."""

        if not self.approval_service_client:
            return

        if not self.approved_entities:
            return

        approval_entity = self.approved_entities[node.id]

        self.approval_service_client.update_copy_status(approval_entity, copy_status)

    def exclude_nodes(self, source_folder: Node, nodes: NodeList) -> Set[str]:
        """Return set of geids that should be excluded when copying from this source folder."""
        if self.approved_entities is not None:
            excluded_geids = nodes.ids.difference(self.approved_entities.geids)
            return excluded_geids

        if self.include_ids is None:
            return set()

        if not self.include_ids.issubset(nodes.ids):
            return set()
        excluded_geids = nodes.ids.difference(self.include_ids)

        return excluded_geids

    def process_file(self, source_file: Node, destination_folder: Union[Path, Node]) -> None:
        """Process one file."""

        raise NotImplementedError

    def process_folder(self, source_folder: Node, destination_parent_folder: Union[Path, Node]) -> Union[Path, Node]:
        """Process one folder."""

        raise NotImplementedError


class CopyManager(BaseCopyManager):
    """Manager to copying files."""

    def __init__(
        self,
        metadata_service_client: MetadataServiceClient,
        cataloguing_service_client: CataloguingServiceClient,
        provenance_service_client: ProvenanceServiceClient,
        dataops_utility_client: DataopsUtilityClient,
        approval_service_client: Optional[ApprovalServiceClient],
        approved_entities: Optional[ApprovedApprovalEntities],
        duplicated_files: DuplicatedFileNames,
        system_tags: List[str],
        project: Node,
        operator: str,
        minio_client: MinioBoto3Client,
        core_zone_label: str,
        green_zone_label: str,
        pipeline_name: str,
        pipeline_desc: str,
        operation_type: str,
        include_geids: Optional[Set[str]],
        kafka_client: KafkaProducer,
    ) -> None:
        super().__init__(metadata_service_client, approval_service_client, approved_entities, include_geids)

        self.cataloguing_service_client = cataloguing_service_client
        self.provenance_service_client = provenance_service_client
        self.dataops_utility_client = dataops_utility_client

        self.duplicated_files = duplicated_files
        self.system_tags = system_tags
        self.project_code = project['code']
        self.operator = operator
        self.minio_client = minio_client
        self.core_zone_label = core_zone_label
        self.green_zone_label = green_zone_label
        self.pipeline_name = pipeline_name
        self.pipeline_desc = pipeline_desc
        self.operation_type = operation_type
        self.kafka_client = kafka_client

    def _create_file_metadata(self, source_node: Node, target_node: Node, new_node_version_id: str) -> None:
        self._copy_zip_preview_info(source_node.id, target_node.id)

        namespace = self.core_zone_label.lower()
        self.cataloguing_service_client.create_catalog_entity(target_node, self.operator, namespace)

        self.provenance_service_client.create_lineage_v3(
            source_node.id,
            target_node.id,
            source_node.name,
            target_node.name,
            self.project_code,
            self.pipeline_name,
            self.pipeline_desc,
        )

        self.kafka_client.create_file_operation_logs(source_node, self.operation_type, self.operator, target_node)

        update_json = {
            'system_tags': self.system_tags,
            'version': new_node_version_id,
        }
        self.metadata_service_client.update_node(source_node, update_json)

    def _copy_zip_preview_info(self, old_geid, new_geid) -> None:
        """Transfer the saved preview info to copied one."""

        response = self.dataops_utility_client.get_zip_preview(old_geid)
        if response is None:
            return

        self.dataops_utility_client.create_zip_preview(new_geid, response['result'])

    def process_file(self, source_file: Node, destination_folder: Node) -> None:
        if not self._is_node_approved(source_file):
            return

        logger.info(f'Processing source file "{source_file}" against destination folder "{destination_folder}".')
        destination_filename = self.duplicated_files.get(source_file.display_path, source_file.name)

        node, version_id = self.metadata_service_client.create_file_node(
            self.project_code,
            source_file,
            destination_folder,
            destination_folder.display_path,
            self.minio_client,
            source_file.tags,
            source_file.get_attributes(),
            new_name=destination_filename,
            system_tags=self.system_tags,
        )

        self._create_file_metadata(source_file, node, version_id)

        self._update_approval_entity_copy_status_for_node(source_file, CopyStatus.COPIED)

    def process_folder(self, source_folder: Node, destination_parent_folder: Node) -> Node:
        logger.info(
            f'Processing source folder "{source_folder}" '
            f'against destination parent folder "{destination_parent_folder}".'
        )
        destination_folder_path = destination_parent_folder.display_path / source_folder.name
        node = self.metadata_service_client.get_node(self.core_zone_label, self.project_code, destination_folder_path)
        if not node:
            node = self.metadata_service_client.create_folder_node(
                self.project_code,
                source_folder,
                destination_parent_folder,
                source_folder.tags,
                system_tags=self.system_tags,
            )

        return node


class CopyPreparationManager(BaseCopyManager):
    """Manager to prepare data before start of copying process."""

    def __init__(
        self,
        metadata_service_client: MetadataServiceClient,
        approval_service_client: Optional[ApprovalServiceClient],
        approved_entities: Optional[ApprovedApprovalEntities],
        project_code: str,
        source_zone: str,
        destination_zone: str,
        source_bucket: Path,
        destination_bucket: Path,
        include_geids: Optional[Set[str]],
    ) -> None:
        super().__init__(metadata_service_client, approval_service_client, approved_entities, include_geids)

        self.project_code = project_code
        self.source_zone = source_zone
        self.destination_zone = destination_zone
        self.source_bucket = source_bucket
        self.destination_bucket = destination_bucket

        self.duplicated_files = DuplicatedFileNames()
        self.read_lock_paths = []
        self.write_lock_paths = []

    def process_file(self, source_file: Node, destination_path: Path) -> None:
        if not self._is_node_approved(source_file):
            return
        logger.info(f'Processing source file "{source_file}" against destination path "{destination_path}".')

        source_filepath = self.source_bucket / source_file.display_path
        destination_filepath = self.destination_bucket / destination_path / source_file.name
        destination_path = destination_path / source_file.name
        if self.metadata_service_client.is_file_exists(self.destination_zone, self.project_code, destination_path):
            source_file['name'] = self.duplicated_files.add(source_file.display_path)
            destination_filepath = self.destination_bucket / destination_path / source_file.name
        self.read_lock_paths.append(source_filepath)
        self.write_lock_paths.append(destination_filepath)

    def process_folder(self, source_folder: Node, destination_parent_path: Path) -> Path:
        logger.info(
            f'Processing source folder "{source_folder}" '
            f'against destination parent path "{destination_parent_path}".'
        )

        source_path = self.source_bucket / source_folder.display_path
        destination_path = self.destination_bucket / destination_parent_path / source_folder.name

        self.read_lock_paths.append(source_path)
        self.write_lock_paths.append(destination_path)

        return destination_parent_path / source_folder.name


class DeleteManager(NodeManager):
    """Manager to deleting files."""

    def __init__(
        self,
        metadata_service_client: MetadataServiceClient,
        cataloguing_service_client: CataloguingServiceClient,
        provenance_service_client: ProvenanceServiceClient,
        dataops_utility_client: DataopsUtilityClient,
        project: Node,
        operator: str,
        minio_client: MinioBoto3Client,
        core_zone_label: str,
        green_zone_label: str,
        pipeline_name: str,
        pipeline_desc: str,
        operation_type: str,
        include_geids: Optional[Set[str]],
        kafka_client: KafkaProducer,
    ) -> None:
        super().__init__(metadata_service_client)

        self.cataloguing_service_client = cataloguing_service_client
        self.provenance_service_client = provenance_service_client
        self.dataops_utility_client = dataops_utility_client

        self.removal_timestamp = get_timestamp()
        self.project_code = project['code']
        self.operator = operator
        self.minio_client = minio_client
        self.core_zone_label = core_zone_label
        self.green_zone_label = green_zone_label
        self.pipeline_name = pipeline_name
        self.pipeline_desc = pipeline_desc
        self.operation_type = operation_type
        self.include_geids = include_geids
        self.kafka_client = kafka_client

    def exclude_nodes(self, source_folder: Node, nodes: NodeList) -> Set[str]:
        if self.include_geids is None:
            return set()

        if not self.include_geids.issubset(nodes.ids):
            return set()

        excluded_geids = nodes.ids.difference(self.include_geids)

        return excluded_geids

    def process_file(self, source_file: Node, destination_folder: Node) -> None:
        logger.info(f'Processing source file "{source_file}" against destination folder "{destination_folder}".')

    def process_folder(self, source_folder: Node, destination_parent_folder: Node) -> Node:
        logger.info(
            f'Processing source folder "{source_folder}" '
            f'against destination parent folder "{destination_parent_folder}".'
        )

    def archive_nodes(self) -> None:
        for node_id in self.include_geids:
            logger.info(f'Move the node "{node_id}" into trashbin recursively')
            node = self.metadata_service_client.get_item_by_id(node_id)
            self.metadata_service_client.archived_node(
                node, self.minio_client, self.kafka_client, self.operation_type, self.operator
            )


class DeletePreparationManager(NodeManager):
    """Manager to prepare data before start of deleting process."""

    def __init__(
        self,
        metadata_service_client: MetadataServiceClient,
        project_code: str,
        source_zone: str,
        source_bucket: Path,
        include_geids: Optional[Set[str]],
    ) -> None:
        super().__init__(metadata_service_client)

        self.project_code = project_code
        self.source_zone = source_zone
        self.source_bucket = source_bucket
        self.include_geids = include_geids

        self.duplicated_files = DuplicatedFileNames()
        self.write_lock_paths = []

    def exclude_nodes(self, source_folder: Node, nodes: NodeList) -> Set[str]:
        if self.include_geids is None:
            return set()

        if not self.include_geids.issubset(nodes.ids):
            return set()

        excluded_geids = nodes.ids.difference(self.include_geids)

        return excluded_geids

    def process_file(self, source_file: Node, destination_path: Path) -> None:
        logger.info(f'Processing source file "{source_file}" against destination path "{destination_path}".')

        source_filepath = self.source_bucket / source_file.display_path

        self.write_lock_paths.append(source_filepath)

    def process_folder(self, source_folder: Node, destination_parent_path: Path) -> Path:
        logger.info(
            f'Processing source folder "{source_folder}" '
            f'against destination parent path "{destination_parent_path}".'
        )

        source_path = self.source_bucket / source_folder.display_path

        self.write_lock_paths.append(source_path)

        return destination_parent_path
