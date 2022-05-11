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

import random
import uuid
from typing import Callable

import pytest
from operations.models import Node
from operations.models import ResourceType


@pytest.fixture
def create_node(fake) -> Callable[..., Node]:
    def _create_node(
        id_=None,
        parent=None,
        parent_path=None,
        name=None,
        type_=None,
        zone=0,
        size=0,
        owner='testuser',
        container_code='testproject',
        container_type='project',
        created_time='2021-05-17 17:19:51.806591',
        last_updated_time='2021-05-17 17:19:51.806591',
        archived=False,
        tags=None,
        attributes=None,
    ) -> Node:
        if id_ is None:
            id_ = fake.pyint()

        if parent is None:
            parent = f'{uuid.uuid4()}'

        if parent_path is None:
            parent_path = 'fake'

        if name is None:
            name = fake.word()

        if type_ is None:
            type_ = random.choice(list(ResourceType))

        if tags is None:
            tags = fake.words()

        if attributes is None:
            attributes = {}

        return Node(
            {
                'id': id_,
                'parent': parent,
                'parent_path': parent_path,
                'restore_path': 'None',
                'archived': archived,
                'type': type_,
                'zone': zone,
                'name': name,
                'size': size,
                'owner': owner,
                'container_code': container_code,
                'container_type': container_type,
                'created_time': created_time,
                'last_updated_time': last_updated_time,
                'storage': {'id': 'fake_id', 'location_uri': 'minio_path', 'version': 'fake_version'},
                'extended': {'id': 'fake_id', 'extra': {'tags': [], 'system_tags': [], 'attributes': attributes}},
            }
        )

    return _create_node
