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

from typing import Tuple

import requests
from config import ConfigClass
from requests import Response


def create_file_node(
    project_code,
    source_file,
    parent_object,
    new_file_object,
    tags=None,
    attribute=None,
    new_name=None,
    extra_fields=None,
) -> Tuple[dict, Response, str]:
    if tags is None:
        tags = source_file['extended']['extra'].get('tags', [])

    if attribute is None:
        attribute = {}

    if extra_fields is None:
        extra_fields = {}

    file_name = new_name if new_name else source_file.get('name')
    # format minio object path
    full_path = '{}/{}'.format(format_folder_path(parent_object, '/'), file_name)

    minio_http = ('https://' if ConfigClass.MINIO_HTTPS else 'http://') + ConfigClass.MINIO_ENDPOINT
    location = 'minio://%s/%s/%s' % (minio_http, 'gr-' + project_code, full_path)

    payload = {
        'parent': parent_object.get('id'),
        'parent_path': format_folder_path(parent_object, '.'),
        'type': 'file',
        'zone': 0,
        'name': file_name,
        'size': source_file.get('size', 0),
        'owner': source_file.get('owner'),
        'container_code': project_code,
        'container_type': 'project',
        'location_uri': location,
        'version': new_file_object.version_id,
        'tags': tags,
    }

    # adding the attribute set if exist
    manifest = source_file['extended']['extra'].get('attributes')
    if manifest:
        payload['manifest_id'] = manifest

    new_file_node = create_node_with_parent(payload)

    return new_file_node


def format_folder_path(node, divider):
    parent_path = node.get('parent_path', None)
    if parent_path:
        path = parent_path.replace('.', divider) if '.' in parent_path else parent_path
        return '{}{}{}'.format(path, divider, node.get('name'))
    return node.get('name')


# this function will help to create a target node
# and connect to parent with "own" relationship
def create_node_with_parent(node_property) -> Tuple[dict, Response]:
    # create the node with following attribute
    # - create_by: who import the files
    # - size: file size in byte (if it is a folder then size will be -1)
    # - location: indicate the minio location as minio://http://<domain>/object
    create_node_url = ConfigClass.METADATA_SERVICE_V1 + 'item/'
    response = requests.post(create_node_url, json=node_property)
    new_node = response.json()['result']

    return new_node


def get_item_node(file_path, project_code, env):
    item_list = file_path['path'].split('/')
    if len(item_list) < 2:
        raise Exception('Invalid dcmedit path')
    else:
        folder_parent = item_list[:-1]
        parent, node_name = '.'.join(folder_parent), item_list[-1]

    item_zone = {'greenroom': 0, 'core': 1}.get(env)
    parameters = {
        'archived': False,
        'zone': item_zone,
        'container_code': project_code,
        'container_type': 'project',
        'recursive': False,
        'parent_path': parent,
        'name': node_name,
    }
    node_query_url = ConfigClass.METADATA_SERVICE_V1 + 'items/search/'
    try:
        response = requests.get(node_query_url, params=parameters)
        ffs = response.json()['result']
        return ffs
    except Exception:
        raise Exception('Item node not found')
