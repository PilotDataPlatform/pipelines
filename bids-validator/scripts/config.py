import os
from functools import lru_cache
from typing import Any
from typing import Dict

from common import VaultClient
from dotenv import load_dotenv
from pydantic import BaseSettings
from pydantic import Extra

# load env var from local env file for local test
load_dotenv()
SRV_NAMESPACE = os.environ.get('APP_NAME', 'service_dataset')
CONFIG_CENTER_ENABLED = os.environ.get('CONFIG_CENTER_ENABLED', 'false')


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        vc = VaultClient(os.getenv('VAULT_URL'), os.getenv('VAULT_CRT'), os.getenv('VAULT_TOKEN'))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    port: int = 5081
    host: str = '127.0.0.1'
    env: str = ''
    version: str = '0.2.0'
    namespace: str = ''

    MINIO_OPENID_CLIENT: str = ''
    MINIO_ENDPOINT: str = ''
    MINIO_HTTPS: str = ''
    KEYCLOAK_MINIO_SECRET: str
    KEYCLOAK_ENDPOINT: str

    # temp path
    DATA_OPS_UT: str = ''
    DATA_OPS_UT_V2: str = ''

    DATASET_SERVICE: str = ''
    QUEUE_SERVICE: str = ''

    RDS_DBNAME: str = ''
    RDS_HOST: str = ''
    RDS_USER: str = ''
    RDS_PWD: str = ''
    SQL_DB_NAME: str = ''

    METADATA_SERVICE_V1: str = ''

    def __init__(self):
        super().__init__()
        self.MINIO_HTTPS = self.MINIO_HTTPS == 'True'
        self.DATA_OPS_UT = self.DATA_OPS_UTIL + '/v1/'
        self.DATA_OPS_UT_V2 = self.DATA_OPS_UTIL + '/v2/'
        self.DATASET_SERVICE += '/v1'
        self.QUEUE_SERVICE += '/v1/'
        self.METADATA_SERVICE_V1 = self.METADATA_SERVICE + '/v1/'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (load_vault_settings, env_settings, init_settings, file_secret_settings)


@lru_cache()
def get_settings():
    settings = Settings()
    return settings


ConfigClass = Settings()
