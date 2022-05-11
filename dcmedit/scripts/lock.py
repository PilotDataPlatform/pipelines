# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

import requests
from config import ConfigClass


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
