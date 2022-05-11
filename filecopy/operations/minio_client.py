import requests
from minio import Minio
from minio.commonconfig import CopySource
from minio.credentials.providers import ClientGrantsProvider


class MinioClient:
    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        s3_host: str,
        s3_endpoint: str,
        is_secure: bool,
        client_secret: str,
        keycloak_endpoint: str,
    ) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.s3_host = s3_host
        self.s3_endpoint = s3_endpoint
        self.is_secure = is_secure
        self.client_secret = client_secret
        self.keycloak_endpoint = keycloak_endpoint

        credentials = self.get_provider()

        self.client = Minio(self.s3_host, credentials=credentials, secure=self.is_secure)

    def check_connection(self):
        """A sanity check for the token to see if the token is expired."""

        self.client.list_buckets()

    def _get_jwt(self):
        """Function helps to get new token/refresh the token.

        Enable the token exchange with different azp.
        """

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
            'subject_token': self.access_token.replace('Bearer ', ''),
            'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token',
            'requested_token_type': 'urn:ietf:params:oauth:token-type:refresh_token',
            'client_id': 'minio',
            'client_secret': self.client_secret,
        }

        # use http request to fetch from keycloak
        result = requests.post(self.keycloak_endpoint, data=payload, headers=headers)
        if result.status_code != 200:
            raise Exception(f'Token refresh failed with: "{result.text}"')

        self.access_token = result.json().get('access_token')
        self.refresh_token = result.json().get('refresh_token')

        jwt_object = result.json()

        return jwt_object

    def get_provider(self):
        """Retrieve credential provide with tokens.

        It will use the jwt function to refresh token if token expired.
        """

        provider = ClientGrantsProvider(self._get_jwt, self.s3_endpoint)
        return provider

    def copy_object(self, bucket, obj, source_bucket, source_obj):
        result = self.client.copy_object(bucket, obj, CopySource(source_bucket, source_obj))
        return result

    def fput_object(self, bucket_name, object_name, file_path):
        result = self.client.fput_object(bucket_name, object_name, file_path)
        return result
