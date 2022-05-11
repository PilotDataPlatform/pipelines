import datetime
import os
from typing import Any
from typing import Dict
from typing import Optional
from zipfile import ZipFile

import requests
from config import ConfigClass
from requests import Response


class MetaDataFactory:
    def __init__(
        self, project: dict, operator: str, zone: str, pipeline_name: str, pipeline_desc: str, operation_type: str
    ):
        self.project = project
        self.oper = operator
        self.zone = zone
        self.zone_label = {'greenroom': ConfigClass.GR_ZONE_LABEL, 'core': ConfigClass.CORE_ZONE_LABEL}.get(zone)

        self.pipeline_name = pipeline_name
        self.pipeline_desc = pipeline_desc
        self.operation_type = operation_type

    def create_lineage_v3(self, input_geid, output_geid, create_time=None) -> Dict[str, Any]:
        """Create lineage between input and output into atlas."""

        my_url = ConfigClass.PROVENANCE_SERVICE
        payload = {
            'input_geid': input_geid,
            'output_geid': output_geid,
            'project_code': self.project.get('code'),
            'pipeline_name': self.pipeline_name,
            'description': self.pipeline_desc,
        }
        res = requests.post(url=my_url + 'lineage', json=payload)
        if res.status_code == 200:
            return res.json()

        raise Exception(res.text)

    def update_file_operation_logs(self, input_file_path, output_file_path, extra=None) -> Response:
        """The function will create the file or folder activity log in the Elastic Search."""

        if extra is None:
            extra = {}

        # new audit log api
        url_audit_log = ConfigClass.PROVENANCE_SERVICE + 'audit-logs'
        payload_audit_log = {
            'action': self.operation_type,
            'operator': self.oper,
            'target': input_file_path,
            'outcome': output_file_path,
            'resource': 'file',
            'display_name': os.path.basename(input_file_path),
            'project_code': self.project.get('code'),
            'extra': extra,
        }
        res_audit_logs = requests.post(url_audit_log, json=payload_audit_log)
        if res_audit_logs.json().get('code', 400) >= 300:
            raise Exception('Error in update_file_operation_logs ' + str(res_audit_logs.json()))

        return res_audit_logs

    def string_2_timestamp(self, time_string: str) -> int:
        return int(
            datetime.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S')
            .replace(tzinfo=datetime.timezone.utc)
            .timestamp()
        )

    def deprecate_index_in_es(self, geid) -> Response:
        """The function will deprecate the file or folder search index in Elastic Search."""

        es_payload = {
            'global_entity_id': geid,
            'updated_fields': {
                'archived': True,
            },
        }
        # logger_info(f"es delete file payload: {es_payload}")
        es_res = requests.put(ConfigClass.PROVENANCE_SERVICE + 'entity/file', json=es_payload)
        # logger_info(f"es delete trash file response: {es_res.text}")

        return es_res

    def create_es_search_index(self, new_node, src_node, data_type, guid) -> Response:
        """The function will create the file or folder search index in the Elastic Search The searchable field."""
        # change string datetime into timestamp
        new_node['time_lastmodified'] = self.string_2_timestamp(new_node['time_lastmodified'])
        new_node['time_created'] = self.string_2_timestamp(new_node['time_created'])

        # update some necessary field for index
        new_node.update(
            {
                'data_type': data_type,
                'archived': False,
                'location': new_node.get('location', ''),
                'process_pipeline': self.pipeline_name,
                'file_name': new_node.get('name'),
                'guid': guid,
                'atlas_guid': guid,
                'dcm_id': src_node.get('dcm_id', None),
                'zone': self.zone,
                'operator': src_node.get('uploader', None),
                'uploader': src_node.get('uploader', None),
                'file_size': src_node.get('file_size', 0),
                'full_path': new_node.get('location'),
            }
        )

        # TODO create new api for this
        if 'manifest_id' in new_node:
            manifest_id = new_node['manifest_id']
            attributes = []
            res = requests.get(ConfigClass.ENTITY_INFO_SERVICE + f'manifest/{manifest_id}')
            if res.status_code == 200:
                manifest_data = res.json()
                manifest = manifest_data['result']
                sql_attributes = manifest['attributes']

                for sql_attribute in sql_attributes:
                    # mc will be the array list while others are string liked
                    if sql_attribute['type'] == 'multiple_choice':
                        attribute_value = []
                        attribute_value.append(new_node.get('attr_' + sql_attribute['name'], ''))
                    else:
                        attribute_value = new_node.get('attr_' + sql_attribute['name'], '')

                    # then format the es search entity
                    attributes.append(
                        {
                            'attribute_name': sql_attribute['name'],
                            'name': manifest['name'],
                            'value': attribute_value,
                        }
                    )

            new_node.update({'attributes': attributes})

        es_res = requests.post(ConfigClass.PROVENANCE_SERVICE + 'entity/file', json=new_node)
        if es_res.json().get('code') >= 300:
            raise Exception('Error in create_es_search_index ' + str(es_res.json()))

        return es_res

    def create_catalog_entity(self, payload) -> str:
        """Function will create new entity in the Atlas."""

        # add required field
        payload.update({'uploader': self.oper})
        payload.update({'file_name': payload.get('name')})
        payload.update({'path': payload.get('location')})
        payload.update({'namespace': ConfigClass.CORE_ZONE_LABEL.lower()})

        res = requests.post(url=ConfigClass.CATALOGUING_SERVICE_V2 + 'filedata', json=payload)

        if res.status_code == 200:
            json_payload = res.json()
            created_entity = None
            if json_payload['result']['mutatedEntities'].get('CREATE'):
                created_entity = json_payload['result']['mutatedEntities']['CREATE'][0]
            elif json_payload['result']['mutatedEntities'].get('UPDATE'):
                created_entity = json_payload['result']['mutatedEntities']['UPDATE'][0]
            if created_entity:
                guid = created_entity['guid']
                return guid

        raise Exception('error create_catalog_entity')


def update_job(
    session_id: str, job_id: str, status: str, add_payload: Optional[Dict[str, Any]] = None, progress: int = 0
) -> None:
    if add_payload is None:
        add_payload = {}

    url = ConfigClass.DATA_OPS_UT_V1 + 'tasks'
    requests.put(
        url,
        json={
            'session_id': session_id,
            'job_id': job_id,
            'status': status,
            'add_payload': add_payload,
            'progress': progress,
        },
    )


def get_job(job_id):
    url = ConfigClass.DATA_OPS_UT_V1 + 'tasks'
    task_response = requests.get(
        url,
        params={
            'session_id': '*',
            'job_id': job_id,
        },
    )
    my_task = task_response.json()['result'][0]
    return my_task


def get_session_id(job_id):
    job = get_job(job_id)
    return job['session_id']


def parse_zip(file_path, type_='zip'):
    results = {}
    if type_ == 'zip':
        ArchiveFile = ZipFile

    with ArchiveFile(file_path, 'r') as archive:
        for file in archive.infolist():
            # get filename for file
            filename = file.filename.split('/')[-1]
            if not filename:
                # get filename for folder
                filename = file.filename.split('/')[-2]
            current_path = results
            for path in file.filename.split('/')[:-1]:
                if path:
                    if not current_path.get(path):
                        current_path[path] = {'is_dir': True}
                    current_path = current_path[path]

            if not file.is_dir():
                current_path[filename] = {
                    'filename': filename,
                    'size': file.file_size,
                    'is_dir': False,
                }
    return results


def save_preview(zip_preview, file_geid):
    try:
        # Store zip file preview in postgres
        payload = {
            'archive_preview': zip_preview,
            'file_geid': file_geid,
        }
        requests.post(ConfigClass.DATA_OPS_UT_V1 + 'archive', json=payload)
    except Exception as e:
        raise e
