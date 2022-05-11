import os
from typing import Any
from typing import Dict

from requests import Session


class ProvenanceServiceClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint_v1 = f'{endpoint}/v1'
        self.client = Session()

    def create_lineage_v3(
        self, input_geid: str, output_geid: str, project_code: str, pipeline_name: str, pipeline_description: str
    ) -> Dict[str, Any]:
        """Create lineage between input and output into atlas.

        Lineage link between greenroom -> relation -> core.
        """

        payload = {
            'input_geid': input_geid,
            'output_geid': output_geid,
            'project_code': project_code,
            'pipeline_name': pipeline_name,
            'description': pipeline_description,
        }

        response = self.client.post(f'{self.endpoint_v1}/lineage/', json=payload)
        if response.status_code != 200:
            raise Exception(f'Unable to create lineage between "{input_geid} and "{output_geid}" in atlas.')

        return response.json()

    def update_file_operation_logs(
        self, input_file_path: str, output_file_path: str, operation_type: str, operator: str, project_code: str
    ) -> Dict[str, Any]:
        """Create the file or folder stream/operational activity log in the Elasticsearch."""

        payload = {
            'action': operation_type,
            'operator': operator,
            'target': input_file_path,
            'outcome': output_file_path,
            'resource': 'file',
            'display_name': os.path.basename(input_file_path),
            'project_code': project_code,
            'extra': {},
        }
        response = self.client.post(f'{self.endpoint_v1}/audit-logs', json=payload)
        if response.status_code != 200:
            raise Exception(
                'Unable to create activity log in the Elasticsearch for'
                f'"{input_file_path}" and "{output_file_path}".'
            )

        return response.json()

    def deprecate_index_in_es(self, geid: str) -> Dict[str, Any]:
        """Deprecate the file or folder search index in Elasticsearch."""

        payload = {
            'global_entity_id': geid,
            'updated_fields': {
                'archived': True,
            },
        }
        response = self.client.put(f'{self.endpoint_v1}/entity/file', json=payload)
        if response.status_code != 200:
            raise Exception(f'Unable to deprecate search index in the Elasticsearch for "{geid}".')

        return response.json()

    def create_index_in_es(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create the file or folder search index in Elasticsearch."""

        response = self.client.post(f'{self.endpoint_v1}/entity/file', json=payload)
        if response.status_code != 200:
            raise Exception(f'Unable to create search index in the Elasticsearch for "{payload}".')

        return response.json()
