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

from functools import lru_cache
from typing import Any
from typing import Dict
from typing import Optional

from common import VaultClient
from pydantic import BaseSettings
from pydantic import Extra


class VaultConfig(BaseSettings):
    """Store vault related configuration."""

    APP_NAME: str = 'pipelines'
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

    APP_NAME: str = 'pipelines'

    MINIO_HTTPS: bool
    MINIO_PORT: int
    MINIO_HOST: str = ''
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str

    RDS_SCHEMA: str = 'pilot_approval'
    RDS_DBNAME: str = ''
    RDS_HOST: str = ''
    RDS_PORT: int
    RDS_USER: str
    RDS_PWD: str

    PROVENANCE_SERVICE: str
    DATAOPS_SERVICE: str
    CATALOGUING_SERVICE: str
    GREEN_ZONE_LABEL: str
    CORE_ZONE_LABEL: str
    METADATA_SERVICE: str

    TEMP_DIR: str = ''
    COPIED_WITH_APPROVAL_TAG: str = 'copied-to-core'
    PROJECT_SERVICE: str
    REDIS_USER: str = 'default'
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: str
    KAFKA_URL: str

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
