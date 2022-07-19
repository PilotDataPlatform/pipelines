# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero
# General Public License as published by the Free Software Foundation,
# either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

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
SRV_NAMESPACE = os.environ.get('APP_NAME', 'bids_validator')
CONFIG_CENTER_ENABLED = os.environ.get('CONFIG_CENTER_ENABLED', 'false')


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        vc = VaultClient(os.getenv('VAULT_URL'), os.getenv('VAULT_CRT'), os.getenv('VAULT_TOKEN'))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    MINIO_HOST: str = ''
    MINIO_PORT: str = ''
    S3_INTERNAL_HTTPS: bool
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    DATAOPS_SERVICE: str = ''
    DATASET_SERVICE: str = ''
    QUEUE_SERVICE: str = ''
    METADATA_SERVICE: str = ''

    DATASET_RDS_DBNAME: str = 'dataset'
    RDS_HOST: str = ''
    RDS_PORT: int
    RDS_USER: str = ''
    RDS_PWD: str = ''

    def __init__(self):
        super().__init__()
        self.DATAOPS_SERVICE += '/v2/'
        self.DATASET_SERVICE += '/v1'
        self.QUEUE_SERVICE += '/v1/'
        self.METADATA_SERVICE = self.METADATA_SERVICE + '/v1/'
        self.DATASET_RDS_URL = (
            f'postgresql://{self.RDS_USER}:{self.RDS_PWD}@{self.RDS_HOST}' f':{self.RDS_PORT}/{self.DATASET_RDS_DBNAME}'
        )
        self.MINIO_URL = f'{self.MINIO_HOST}:{self.MINIO_PORT}'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (env_settings, load_vault_settings, init_settings, file_secret_settings)


@lru_cache()
def get_settings():
    settings = Settings()
    return settings


ConfigClass = Settings()
