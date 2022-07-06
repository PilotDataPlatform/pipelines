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
from enum import Enum
from enum import unique
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from requests import Session

logger = logging.getLogger(__name__)


@unique
class ResourceLockOperation(str, Enum):
    READ = 'read'
    WRITE = 'write'

    class Config:
        use_enum_values = True


@unique
class JobStatus(str, Enum):
    SUCCEED = 'SUCCEED'
    TERMINATED = 'TERMINATED'

    class Config:
        use_enum_values = True


class DataopsUtilityClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint_v1 = f'{endpoint}/v1'
        self.endpoint_v2 = f'{endpoint}/v2'
        self.client = Session()

    def lock_resources(self, resource_keys: List[Path], operation: ResourceLockOperation) -> Dict[str, Any]:
        resource_keys = list(map(str, resource_keys))

        logger.info(
            f'Performing "{operation}" \
            lock for resource keys: {resource_keys}.'
        )
        response = self.client.post(
            f'{self.endpoint_v2}/resource/lock/bulk',
            json={
                'resource_keys': resource_keys,
                'operation': operation,
            },
        )

        if response.status_code != 200:
            message = f'Unable to lock resource keys: {resource_keys}.'
            logger.info(message)
            raise Exception(message)

        logger.info(
            f'Successfully "{operation}" \
            locked resource keys: {resource_keys}.'
        )
        return response.json()

    def unlock_resources(self, resource_keys: List[Path], operation: ResourceLockOperation) -> Dict[str, Any]:
        resource_keys = list(map(str, resource_keys))

        logger.info(
            f'Performing "{operation}" \
            unlock for resource keys: {resource_keys}.'
        )
        response = self.client.delete(
            f'{self.endpoint_v2}/resource/lock/bulk',
            json={
                'resource_keys': resource_keys,
                'operation': operation,
            },
        )

        if response.status_code not in (200, 400):
            message = f'Unable to unlock resource keys: {resource_keys}.'
            logger.info(message)
            raise Exception(message)

        logger.info(
            f'Successfully "{operation}" \
            unlocked resource keys: {resource_keys}.'
        )
        return response.json()

    def update_job(self, session_id: str, job_id: str, status: JobStatus) -> Dict[str, Any]:
        response = self.client.put(
            f'{self.endpoint_v1}/tasks/',
            json={
                'session_id': session_id,
                'job_id': job_id,
                'status': status,
            },
        )

        if response.status_code != 200:
            logger.error(
                f'Unexpected status code received while updating job"{job_id}" Received response: "{response.text}".'
            )
            raise Exception(f'Unable to update job "{job_id}".')

        return response.json()

    def get_zip_preview(self, file_geid: str) -> Optional[Dict[str, Any]]:
        response = self.client.get(
            f'{self.endpoint_v1}/archive',
            params={
                'file_id': file_geid,
            },
        )
        if response.status_code == 404:
            return None

        if response.status_code != 200:
            logger.error(
                'Unexpected status code received while getting zip preview '
                f'for geid "{file_geid}". '
                f'Received response: "{response.text}".'
            )
            raise Exception(f'Unable to get zip preview for id "{file_geid}"')

        return response.json()

    def create_zip_preview(self, file_id: str, archive_preview: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.post(
            f'{self.endpoint_v1}/archive',
            json={
                'file_id': file_id,
                'archive_preview': archive_preview,
            },
        )

        if response.status_code != 200:
            logger.error(
                'Unexpected status code received while creating zip '
                f'preview for geid "{file_id}". '
                f'Received response: "{response.text}".'
            )
            raise Exception(
                f'Unable to create zip preview for id \
                "{file_id}"'
            )

        return response.json()
