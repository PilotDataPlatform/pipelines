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
from typing import Any
from typing import Dict

from requests import Session

logger = logging.getLogger(__name__)


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
        response = self.client.post(f'{self.endpoint_v1}/lineage/', json=payload, timeout=300)
        logger.debug(response.json())
        if response.status_code != 200:
            raise Exception(f'Unable to create lineage between "{input_id} and "{output_id}" in atlas.')

        return response.json()
