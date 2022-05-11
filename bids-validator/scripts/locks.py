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

import requests
from config import ConfigClass


def get_all_children_nodes(parent_path, zone, container_code):

    item_zone = {'greenroom': 0, 'core': 1}.get(zone)
    parameters = {
        'archived': False,
        'zone': item_zone,
        'container_code': container_code,
        'container_type': 'dataset',
        'recursive': True,
    }
    if parent_path:
        parameters['parent_path'] = parent_path

    node_query_url = ConfigClass.METADATA_SERVICE_V1 + 'items/search/'
    response = requests.get(node_query_url, params=parameters)
    ffs = response.json()['result']

    return ffs


def lock_resource(resource_key: str, operation: str) -> dict:
    # operation can be either read or write
    url = ConfigClass.DATA_OPS_UT_V2 + 'resource/lock'
    post_json = {'resource_key': resource_key, 'operation': operation}

    response = requests.post(url, json=post_json)
    if response.status_code != 200:
        raise Exception('resource %s already in used' % resource_key)

    return response.json()


def unlock_resource(resource_key: str, operation: str) -> dict:
    # operation can be either read or write
    url = ConfigClass.DATA_OPS_UT_V2 + 'resource/lock'
    post_json = {'resource_key': resource_key, 'operation': operation}

    response = requests.delete(url, json=post_json)
    if response.status_code != 200:
        raise Exception('Error when unlock resource %s' % resource_key)

    return response.json()


def format_folder_path(node):
    parent_path = node.get('parent_path', None)
    if parent_path:
        path = parent_path.replace('.', '/') if '.' in parent_path else parent_path
        return '{}/{}'.format(path, node.get('name'))
    return node.get('name')


def lock_nodes(dataset_code: str):
    """the function will recursively lock the node tree."""

    # this is for crash recovery, if something trigger the exception
    # we will unlock the locked node only. NOT the whole tree. The example
    # case will be copy the same node, if we unlock the whole tree in exception
    # then it will affect the processing one.
    locked_node, err = [], None

    try:
        nodes = get_all_children_nodes(None, 'core', dataset_code)
        for ff_object in nodes:
            # we will skip the deleted nodes
            if ff_object.get('archived', False):
                continue

            # conner case here, we DONT lock the name folder
            # for the copy we will lock the both source and target
            if ff_object.get('type') == 'file':
                location = ff_object.get('storage')['location_uri']
                minio_path = location.split('//')[-1]
                _, bucket, minio_obj_path = tuple(minio_path.split('/', 2))
            else:
                bucket = ff_object.get('container')
                minio_obj_path = format_folder_path(ff_object)

            source_key = '{}/{}'.format(bucket, minio_obj_path)
            lock_resource(source_key, 'read')
            locked_node.append((source_key, 'read'))

    except Exception as e:
        err = e

    return locked_node, err
