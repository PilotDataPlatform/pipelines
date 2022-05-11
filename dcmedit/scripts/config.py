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
SRV_NAMESPACE = os.environ.get('APP_NAME', 'all')
CONFIG_CENTER_ENABLED = os.environ.get('CONFIG_CENTER_ENABLED', 'false')


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        vc = VaultClient(os.getenv('VAULT_URL'), os.getenv('VAULT_CRT'), os.getenv('VAULT_TOKEN'))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    env: str = 'test'
    namespace: str = ''
    version = '0.2.0'

    # minio
    MINIO_OPENID_CLIENT: str
    MINIO_ENDPOINT: str
    MINIO_HTTPS: str
    KEYCLOAK_MINIO_SECRET: str
    KEYCLOAK_ENDPOINT: str

    DATA_OPS_UT_V1: str = ''
    DATA_OPS_UT_V2: str = ''
    ENTITY_INFO_SERVICE: str = ''
    PROVENANCE_SERVICE: str
    DATA_OPS_UTIL: str
    CATALOGUING_SERVICE_V2: str = ''
    GR_ZONE_LABEL: str
    CORE_ZONE_LABEL: str
    DCM_PROJECT: str
    METADATA_SERVICE_V1: str = ''

    def __init__(self):
        super().__init__()
        self.MINIO_HTTPS = self.MINIO_HTTPS == 'True'
        self.DATA_OPS_UT_V1 = self.DATA_OPS_UTIL + '/v1/'
        self.DATA_OPS_UT_V2 = self.DATA_OPS_UTIL + '/v2/'
        self.ENTITY_INFO_SERVICE = self.ENTITYINFO_SERVICE + '/v1/'
        self.PROVENANCE_SERVICE += '/v1/'
        self.CATALOGUING_SERVICE_V2 = self.CATALOGUING_SERVICE + '/v2/'
        self.METADATA_SERVICE_V1 = self.METADATA_SERVICE + '/v1/'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (init_settings, load_vault_settings, env_settings, file_secret_settings)


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigClass = Settings()
