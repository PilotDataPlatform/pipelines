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
import io
from datetime import datetime
from typing import Optional

from aiokafka import AIOKafkaProducer
from fastavro import schema
from fastavro import schemaless_writer
from models import Node


class KafkaProducer:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
        self.topic = 'items-activity-logs'
        self.schema = 'item_activity_schema.avsc'

    def connect_to_kafka(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.endpoint)

    def create_file_operation_logs(
        self, input_file: Node, operation_type: str, operator: str, output_file: Optional[Node]
    ):

        message = {
            'activity_type': operation_type,
            'activity_time': datetime.now(),
            'item_id': input_file.id,
            'item_type': input_file.get('type'),
            'item_name': input_file.name,
            'item_parent_path': input_file.parent_path,
            'container_code': input_file.get('container_code'),
            'container_type': input_file.get('container_type'),
            'zone': input_file.get('zone'),
            'user': operator,
            'imported_from': '',
            'changes': [],
        }

        if operation_type == 'copy':
            message['changes'] = [
                {'item_property': 'path', 'old_value': input_file.display_path, 'new_value': output_file.display_path}
            ]
        loop = asyncio.get_event_loop()
        try:
            # Validate message
            bio = io.BytesIO()
            SCHEMA = schema.load_schema(self.schema)
            schemaless_writer(bio, SCHEMA, message)

            validated_message = bio.getvalue()

            # Send message to kafka
            loop.run_until_complete(self.producer.start())
            loop.run_until_complete(self.producer.send_and_wait(self.topic, validated_message))
        except Exception as e:
            raise Exception(f'Error when validate and send message to kafka producer: {e}')

        finally:
            loop.run_until_complete(self.producer.stop())
