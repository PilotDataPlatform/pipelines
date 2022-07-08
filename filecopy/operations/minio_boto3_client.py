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
import math
import os

from common.object_storage_adaptor.boto3_client import Boto3Client
from common.object_storage_adaptor.boto3_client import get_boto3_client

logger = logging.getLogger(__name__)


class MinioBoto3Client:
    def __init__(self, access_token: str, minio_endpoint: str, minio_https: str) -> None:
        self.token = access_token
        self.minio_endpoint = minio_endpoint
        self.minio_https = minio_https
        self.client = self.connect_to_minio()

    def connect_to_minio(self) -> Boto3Client:
        loop = asyncio.get_event_loop()
        boto3_client = loop.run_until_complete(
            get_boto3_client(self.minio_endpoint, token=self.token, https=self.minio_https)
        )
        return boto3_client

    async def download_object(self, src_bucket, src_path, temp_path):
        await self.client.downlaod_object(src_bucket, src_path, temp_path)

    async def copy_object(self, dest_bucket, dest_path, source_bucket, source_path):
        logger.debug(f'Temp credential is {self.client.temp_credentials}')
        result = await self.client.copy_object(source_bucket, source_path, dest_bucket, dest_path)
        return result

    async def upload_object(self, bucket, object_name, file_path):
        # Here get the total size of the size and set up the max size of each chunk
        max_size = 5 * 1024 * 1024
        size = os.path.getsize(file_path)
        logger.info('File total size is ')
        total_parts = math.ceil(size / max_size)

        # Get upload id from upload pre
        upload_id_list = await self.client.prepare_multipart_upload(bucket, [object_name])
        upload_id = upload_id_list[0]
        logger.info(f'The upload id is {upload_id}')
        parts = []
        with open(file_path, 'rb') as f:

            for part_number in range(total_parts):

                # Cut file into chunks and upload the chunk
                file_data = f.read(max_size)
                chunk_result = await self.client.part_upload(bucket, object_name, upload_id, part_number + 1, file_data)
                parts.append(chunk_result)
                logger.info(f'Chunk upload result {chunk_result}')
        res = await self.client.combine_chunks(bucket, object_name, upload_id, parts)
        logger.info(f'Finalize the large file upload with version is {res}')
        return res

    async def remove_object(self, src_bucket, src_obj_path):
        result = await self.client.delete_object(src_bucket, src_obj_path)
        return result
