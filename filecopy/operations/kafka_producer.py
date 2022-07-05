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

import io
from datetime import datetime
from typing import Optional

from aiokafka import AIOKafkaProducer
from fastavro import schema
from fastavro import schemaless_writer
from operations.models import Node


class KafkaProducer:
    def __init__(self, endpoint) -> None:
        self.endpoint = endpoint
        self.topic = 'metadata.items.activity'
        self.schema = 'operations/item_activity_schema.avsc'

    async def init_connection(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.endpoint)

    async def create_file_operation_logs(
        self, input_file: Node, operation_type: str, operator: str, output_file: Optional[Node]
    ):
        message = {
            'activity_type': operation_type,
            'activity_time': datetime.utcnow(),
            'item_id': input_file.id,
            'item_type': input_file.get('type'),
            'item_name': input_file.name,
            'item_parent_path': ('' if input_file.parent_path is None else input_file.parent_path),
            'container_code': input_file.get('container_code'),
            'container_type': input_file.get('container_type'),
            'zone': input_file.get('zone'),
            'user': operator,
            'imported_from': '',
            'changes': [],
        }

        if operation_type == 'copy':
            message['changes'] = [
                {
                    'item_property': 'path',
                    'old_value': str(input_file.display_path),
                    'new_value': str(output_file.display_path),
                }
            ]
        try:
            # Validate message
            bio = io.BytesIO()
            SCHEMA = schema.load_schema(self.schema)
            schemaless_writer(bio, SCHEMA, message)

            validated_message = bio.getvalue()

            # Send message to kafka
            await self.producer.start()
            await self.producer.send_and_wait(self.topic, validated_message)
        except Exception as e:
            raise Exception(f'Error when validate and send message to kafka producer: {e}')

        finally:
            await self.producer.stop()
