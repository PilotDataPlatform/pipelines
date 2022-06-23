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
    MINIO_ENDPOINT: str = ''
    MINIO_HTTPS: str = ''

    DATA_OPS_UT_V2: str = ''
    DATASET_SERVICE: str = ''
    QUEUE_SERVICE: str = ''

    RDS_DBNAME: str = ''
    RDS_HOST: str = ''
    RDS_USER: str = ''
    RDS_PWD: str = ''
    SQL_DB_NAME: str = ''

    METADATA_SERVICE_V1: str = ''
    SQLALCHEMY_DATABASE_URI: str = ''

    def __init__(self):
        super().__init__()
        self.MINIO_HTTPS = self.MINIO_HTTPS == 'True'
        self.DATA_OPS_UT_V2 = self.DATA_OPS_UTIL + '/v2/'
        self.DATASET_SERVICE += '/v1'
        self.QUEUE_SERVICE += '/v1/'
        self.METADATA_SERVICE_V1 = self.METADATA_SERVICE + '/v1/'
        self.SQLALCHEMY_DATABASE_URI = f'postgresql://{self.RDS_USER}:{self.RDS_PWD}@{self.RDS_HOST}/{self.RDS_DBNAME}'

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
