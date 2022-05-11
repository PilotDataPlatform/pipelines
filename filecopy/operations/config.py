from functools import lru_cache
from typing import Any
from typing import Dict
from typing import Optional

from common import VaultClient
from pydantic import BaseSettings
from pydantic import Extra


class VaultConfig(BaseSettings):
    """Store vault related configuration."""

    APP_NAME: str = 'filecopy'
    CONFIG_CENTER_ENABLED: bool = False

    VAULT_URL: Optional[str]
    VAULT_CRT: Optional[str]
    VAULT_TOKEN: Optional[str]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    config = VaultConfig()

    if not config.CONFIG_CENTER_ENABLED:
        return {}

    client = VaultClient(config.VAULT_URL, config.VAULT_CRT, config.VAULT_TOKEN)
    return client.get_from_vault(config.APP_NAME)


class Settings(BaseSettings):
    """Store service configuration settings."""

    APP_NAME: str = 'filecopy'

    MINIO_OPENID_CLIENT: str
    MINIO_ENDPOINT: str
    MINIO_HTTPS: bool
    MINIO_HOST: str = ''

    KEYCLOAK_MINIO_SECRET: str
    KEYCLOAK_ENDPOINT: str

    RDS_SCHEMA_DEFAULT: str
    RDS_DB_URI: str

    NEO4J_SERVICE: str
    PROVENANCE_SERVICE: str
    DATA_OPS_UTIL: str
    CATALOGUING_SERVICE: str
    GREEN_ZONE_LABEL: str
    CORE_ZONE_LABEL: str
    METADATA_SERVICE: str

    TEMP_DIR: str = ''
    COPIED_WITH_APPROVAL_TAG: str = 'copied-to-core'

    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

        self.MINIO_HOST = self.MINIO_ENDPOINT
        self.MINIO_ENDPOINT = ('https' if self.MINIO_HTTPS else 'http') + f'://{self.MINIO_HOST}'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.ignore

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, load_vault_settings, init_settings, file_secret_settings


@lru_cache(1)
def get_settings() -> Settings:
    settings = Settings()
    return settings
