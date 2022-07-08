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
import logging
import time
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from common import ProjectException
from operations.kafka_producer import KafkaProducer
from operations.minio_boto3_client import MinioBoto3Client
from operations.models import Node
from operations.models import NodeList
from operations.models import ResourceType
from operations.models import ZoneType
from requests import Session

logger = logging.getLogger(__name__)


class MetadataServiceClient:
    def __init__(
        self, endpoint: str, minio_endpoint: str, core_zone_label: str, temp_dir: str, project_client: str
    ) -> None:
        self.endpoint_v1 = f'{endpoint}/v1/'
        self.client = Session()

        self.minio_endpoint = minio_endpoint
        self.core_zone_label = core_zone_label
        self.temp_dir = temp_dir
        self.project_client = project_client

    def get_item_by_id(self, node_id: str) -> Node:
        nodes = self.get_items_by_ids([node_id])
        return nodes[node_id]

    def get_items_by_ids(self, ids: list) -> Dict[str, Node]:
        parameter = {'ids': ids}
        response = self.client.get(f'{self.endpoint_v1}items/batch/', params=parameter)
        if response.status_code != 200:
            raise Exception(f'Unable to get nodes by ids "{ids}".')

        results = response.json()['result']

        if len(results) != len(ids):
            raise Exception(
                f'Number of returned nodes does not match number \
                    of requested ids "{ids}".'
            )

        nodes = {node.id: node for node in NodeList(results)}

        return nodes

    async def get_project_by_code(self, project_code: str) -> Node:
        try:
            project = await self.project_client.get(code=project_code)
            result = await project.json()
        except ProjectException:
            raise ProjectException(f'Unable to get project by code "{project_code}".')

        return Node(result)

    def get_nodes_tree(self, start_folder_id: str, traverse_subtrees: bool = False) -> NodeList:
        parent_folder_response = self.client.get('{}item/{}/'.format(self.endpoint_v1, start_folder_id))
        parent_folder = parent_folder_response.json()['result']
        if parent_folder_response.status_code != 200:
            raise Exception(
                f'Unable to get parent folder starting \
                    from "{start_folder_id}".'
            )

        parameters = {
            'archived': False,
            'zone': parent_folder['zone'],
            'container_code': parent_folder['container_code'],
            'parent_path': self.format_folder_path(parent_folder, '.'),
            'recursive': traverse_subtrees,
        }
        node_query_url = self.endpoint_v1 + 'items/search/'
        response = self.client.get(node_query_url, params=parameters)

        if response.status_code != 200:
            raise Exception(f'Unable to get nodes tree starting from "{start_folder_id}".')

        nodes = NodeList(response.json()['result'])
        return nodes

    def get_node(self, zone: str, project_code: str, file_path: Union[Path, str]) -> Optional[Node]:
        item_list = str(file_path).split('/')
        if len(item_list) < 2:
            raise Exception('Invalid item path')
        else:
            folder_parent = item_list[:-1]
            parent, node_name = '.'.join(folder_parent), item_list[-1]

        item_zone = {'greenroom': 0, 'core': 1}.get(zone.lower())
        parameters = {
            'archived': False,
            'zone': item_zone,
            'container_code': project_code,
            'recursive': False,
            'parent_path': parent,
            'name': node_name,
        }
        node_query_url = self.endpoint_v1 + 'items/search/'
        response = self.client.get(node_query_url, params=parameters)
        node = response.json()['result']
        if node:
            return Node(node[0])
        return None

    def is_file_exists(self, zone: str, project_code: str, path: Union[Path, str]) -> bool:
        """Check if file already exists at specified path."""

        node = self.get_node(zone, project_code, path)

        return bool(node)

    def is_folder_exists(self, zone: str, project_code: str, path: Union[Path, str]) -> bool:
        """Check if folder already exists within project at specified path."""

        node = self.get_node(zone, project_code, path)

        return bool(node)

    def update_node(self, node: Node, update_json: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.put(url=f'{self.endpoint_v1}item/', params={'id': node.get('id')}, json=update_json)

        if response.status_code != 200:
            raise Exception(
                f'Unable to update node with node \
                id "{node["id"]}".'
            )

        return response.json()

    def format_folder_path(self, node: Node, divider: str) -> str:
        parent_path = node.get('parent_path', None)
        if parent_path:
            path = parent_path.replace('.', divider) if '.' in parent_path else parent_path
            return '{}{}{}'.format(path, divider, node.get('name'))
        return node.get('name')

    def create_node_with_parent(self, node_property) -> Node:
        """create the node with following attribute."""
        create_node_url = self.endpoint_v1 + 'item/'
        response = self.client.post(create_node_url, json=node_property)
        new_node = response.json()['result']
        return Node(new_node)

    def move_node_to_trash(self, node_id: str) -> List:
        patch_node_url = self.endpoint_v1 + 'item/'
        parameter = {'id': node_id, 'archived': True}
        response = self.client.patch(patch_node_url, params=parameter)
        trash_node = response.json()['result']
        return trash_node

    def create_file_node(
        self,
        project: str,
        source_file: Node,
        parent_node: Node,
        folder_display_path: Path,
        minio_client: MinioBoto3Client,
        tags: Optional[List] = None,
        attribute: Optional[dict] = None,
        new_name: Optional[str] = None,
        system_tags: Optional[List] = None,
    ) -> Tuple[Node, str]:
        if tags is None:
            tags = []

        if attribute is None:
            attribute = {}

        if system_tags is None:
            system_tags = []

        file_name = new_name if new_name else source_file.get('name')

        file_display_path = folder_display_path / file_name
        location = f'minio://{self.minio_endpoint}/core-{project}/{file_display_path}'

        payload = {
            'parent': parent_node.get('id'),
            'parent_path': self.format_folder_path(parent_node, '.'),
            'type': 'file',
            'zone': ZoneType.CORE,
            'name': file_name,
            'size': source_file.get('size', 0),
            'owner': source_file.get('owner'),
            'container_code': project,
            'container_type': 'project',
            'location_uri': location,
            'version': '',
            'tags': tags,
            'system_tags': system_tags,
            'attributes': attribute,
            # 'attribute_template_id': '',
        }

        # adding the attribute set if exist
        manifest = source_file['extended']['extra'].get('attributes')
        if manifest:
            payload['attribute_template_id'] = list(manifest.keys())[0]
            payload['attributes'] = manifest[list(manifest.keys())[0]]

        try:
            # minio location is
            # minio://http://<end_point>/bucket/user/object_path
            src_minio_path = source_file['storage'].get('location_uri').split('//')[-1]
            _, src_bucket, src_obj_path = tuple(src_minio_path.split('/', 2))
            target_minio_path = location.split('//')[-1]
            _, target_bucket, target_obj_path = tuple(target_minio_path.split('/', 2))

            # here the minio api only accept the 5GB in copy.
            # if >5GB we need to download
            # to local then reupload to target
            file_size_gb = payload['size']
            loop = asyncio.get_event_loop()
            if file_size_gb < 5e9:
                logger.info('File size less than 5GiB')
                logger.info(
                    f'Copying object from "{src_bucket}/{src_obj_path}" to \
                        "{target_bucket}/{target_obj_path}".'
                )
                result = loop.run_until_complete(
                    minio_client.copy_object(target_bucket, target_obj_path, src_bucket, src_obj_path)
                )
                version_id = result.get('VersionId', '')  # empty in case versioning is unsupported
            else:
                logger.info('File size greater than 5GiB')
                temp_path = self.temp_dir + str(time.time())
                loop.run_until_complete(minio_client.download_object(src_bucket, src_obj_path, temp_path))
                logger.info(f'File fetched to local disk: {temp_path}')
                temp_file_path = f"{temp_path}/{payload['name']}"
                result = loop.run_until_complete(
                    minio_client.upload_object(target_bucket, target_obj_path, temp_file_path)
                )
                version_id = result.get('VersionId', '')  # empty in case versioning is unsupported

            logger.info(f'Minio Copy {src_bucket}/{src_obj_path} Success')
            payload['version'] = version_id
            new_file_node = self.create_node_with_parent(payload)
        except Exception:
            logger.exception('Error when copying.')
            raise

        return new_file_node, version_id

    def create_folder_node(
        self,
        project_code: str,
        source_folder: Node,
        parent_node: Node,
        tags: Optional[List[str]] = None,
        new_name: Optional[str] = None,
        system_tags: Optional[List[str]] = None,
    ) -> Node:
        if tags is None:
            tags = []

        if system_tags is None:
            system_tags = []

        folder_name = source_folder.get('name')
        if new_name is not None:
            folder_name = new_name
        # then copy the node under the dataset
        payload = {
            'parent': parent_node.get('id'),
            'parent_path': self.format_folder_path(parent_node, '.'),
            'type': 'folder',
            'zone': ZoneType.CORE,
            'name': folder_name,
            # The folder does not have size
            'size': None,
            'owner': source_folder.get('owner'),
            'container_code': project_code,
            'container_type': 'project',
            # The folder does not have location uri
            'location_uri': '',
            'version': '',
            'tags': tags,
            'system_tags': system_tags,
        }
        folder_node = self.create_node_with_parent(payload)

        return folder_node

    def archived_node(self, source_file: Node, minio_client: MinioBoto3Client, operation_type, operator) -> Node:
        trash_node = self.move_node_to_trash(source_file.id)

        try:
            # minio location is
            # minio://http://<end_point>/bucket/user/object_path
            for item in trash_node:
                if item['type'] == ResourceType.FILE:
                    # Remove from minio
                    src_minio_path = item['storage'].get('location_uri').split('//')[-1]
                    _, src_bucket, src_obj_path = tuple(src_minio_path.split('/', 2))

                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(minio_client.remove_object(src_bucket, src_obj_path))
                    logger.info(
                        f'Minio Delete \
                        {src_bucket}/{src_obj_path} Success'
                    )
                    # Add activity log
                    loop.run_until_complete(
                        KafkaProducer.create_file_operation_logs(Node(item), operation_type, operator, None)
                    )
        except Exception:
            logger.exception('Error when removing file.')
            raise

        return trash_node
