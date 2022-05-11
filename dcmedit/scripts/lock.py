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
