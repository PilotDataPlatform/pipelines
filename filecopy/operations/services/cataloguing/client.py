from operations.models import Node
from requests import Session


class CataloguingServiceClient:
    def __init__(self, endpoint: str):
        self.endpoint_v2 = f'{endpoint}/v2'
        self.client = Session()

    def create_catalog_entity(self, payload: Node, operator: str, namespace: str) -> str:
        """Function will create new entity in the Atlas."""

        payload.update({'uploader': operator})
        payload.update({'file_name': payload.get('name')})
        payload.update({'path': payload.get('location')})
        payload.update({'namespace': namespace})

        response = self.client.post(f'{self.endpoint_v2}/filedata', json=payload)

        if response.status_code != 200:
            raise Exception(f'Unable to create new entity in the Atlas for "{payload}".')

        json_payload = response.json()
        created_entity = None
        if json_payload['result']['mutatedEntities'].get('CREATE'):
            created_entity = json_payload['result']['mutatedEntities']['CREATE'][0]
        elif json_payload['result']['mutatedEntities'].get('UPDATE'):
            created_entity = json_payload['result']['mutatedEntities']['UPDATE'][0]

        if created_entity:
            guid = created_entity['guid']
            return guid
