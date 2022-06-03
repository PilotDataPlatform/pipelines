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

import os
from typing import Any
from typing import Dict

from requests import Session


class ProvenanceServiceClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint_v1 = f'{endpoint}/v1'
        self.client = Session()

    def create_lineage_v3(
        self,
        input_id: str,
        output_id: str,
        input_name: str,
        output_name: str,
        project_code: str,
        pipeline_name: str,
        pipeline_description: str,
    ) -> Dict[str, Any]:
        """Create lineage between input and output into atlas.

        Lineage link between greenroom -> relation -> core.
        """

        payload = {
            'input_id': input_id,
            'output_id': output_id,
            'input_name': input_name,
            'output_name': output_name,
            'project_code': project_code,
            'pipeline_name': pipeline_name,
            'description': pipeline_description,
        }
        response = self.client.post(f'{self.endpoint_v1}/lineage/', json=payload)
        if response.status_code != 200:
            raise Exception(f'Unable to create lineage between "{input_id} and "{output_id}" in atlas.')

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

    def deprecate_index_in_es(self, _id: str) -> Dict[str, Any]:
        """Deprecate the file or folder search index in Elasticsearch."""

        payload = {
            'global_entity_id': _id,
            'updated_fields': {
                'archived': True,
            },
        }
        response = self.client.put(f'{self.endpoint_v1}/entity/file', json=payload)
        if response.status_code != 200:
            raise Exception(f'Unable to deprecate search index in the Elasticsearch for "{_id}".')

        return response.json()

    def create_index_in_es(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create the file or folder search index in Elasticsearch."""

        response = self.client.post(f'{self.endpoint_v1}/entity/file', json=payload)
        if response.status_code != 200:
            raise Exception(f'Unable to create search index in the Elasticsearch for "{payload}".')

        return response.json()
