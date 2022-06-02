# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see http://www.gnu.org/licenses/.

import argparse
import json
import os
import shutil
import subprocess
import time
import traceback
from datetime import datetime

import requests
from config import ConfigClass
from database_service import DatasetModel
from database_service import DBConnection
from locks import lock_nodes
from locks import unlock_resource
from minio_client import Minio_Client_
from sqlalchemy.dialects.postgresql import insert

TEMP_FOLDER = './dataset/'


def debug_message_sender(message: str):
    url = ConfigClass.DATA_OPS_UT + 'files/actions/message'
    response = requests.post(url, json={'message': message, 'channel': 'pipelinewatch'})
    if response.status_code != 200:
        logger_info('code: ' + str(response.status_code) + ': ' + response.text)
    return


def logger_info(message: str):
    debug_message_sender(message)


def parse_inputs() -> dict:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('-d', '--dataset-id', help='Dataset id', required=True)
    parser.add_argument('-env', '--environment', help='Environment', required=True)
    parser.add_argument('-refresh', '--refresh-token', help='Refresh Token', required=True)
    parser.add_argument('-access', '--access-token', help='Access Token', required=True)

    arguments = vars(parser.parse_args())
    return arguments


def get_dataset_code(dataset_id) -> str:
    url = f'{ConfigClass.DATASET_SERVICE}/dataset/{dataset_id}'
    try:
        response = requests.get(url)
        dataset_code = response.json()['result']['code']
        return dataset_code
    except Exception:
        logger_info(f'Fail to get dataset code by {dataset_id}')
        raise


def send_message(dataset_id, status, bids_output) -> None:
    queue_url = ConfigClass.QUEUE_SERVICE + 'broker/pub'
    post_json = {
        'event_type': 'BIDS_VALIDATE_NOTIFICATION',
        'payload': {
            'status': status,  # INIT/RUNNING/FINISH/ERROR
            'dataset': dataset_id,
            'payload': bids_output,
            'update_timestamp': time.time(),
        },
        'binary': True,
        'queue': 'socketio',
        'routing_key': 'socketio',
        'exchange': {'name': 'socketio', 'type': 'fanout'},
    }

    if status == 'failed':
        post_json['payload']['payload'] = None
        post_json['payload']['error_msg'] = bids_output

    try:
        queue_res = requests.post(queue_url, json=post_json)
        if queue_res.status_code != 200:
            logger_info('code: ' + str(queue_res.status_code) + ': ' + queue_res.text)
        logger_info('sent message to queue')
        return
    except Exception as e:
        logger_info(f'Failed to send message to queue: {str(e)}')
        raise


def get_files(dataset_code) -> list:
    all_files = []

    query = {
        'archived': False,
        'zone': 1,
        'container_code': dataset_code,
        'container_type': 'dataset',
        'recursive': True,
    }

    try:
        resp = requests.get(ConfigClass.METADATA_SERVICE_V1 + 'items/search/', params=query)
        for node in resp.json()['result']:
            if node['type'] == 'file':
                all_files.append(node['storage']['location_uri'])
        return all_files
    except Exception as e:
        logger_info(f'Error when get files: {str(e)}')
        raise


def download_from_minio(files_locations, auth_token) -> None:
    mc = Minio_Client_(auth_token['at'], auth_token['rt'])
    logger_info('========Minio_Client Initiated========')

    try:
        for file_location in files_locations:
            minio_path = file_location.split('//')[-1]
            _, bucket, obj_path = tuple(minio_path.split('/', 2))

            mc.client.fget_object(bucket, obj_path, TEMP_FOLDER + obj_path)
        logger_info('========Minio_Client download finished========')

    except Exception as e:
        logger_info(f'Error when download data from minio: {str(e)}')
        raise


def getProcessOutput() -> None:
    f = open('result.txt', 'w')
    try:
        subprocess.run(['bids-validator', TEMP_FOLDER + 'data', '--json'], universal_newlines=True, stdout=f)
    except Exception as e:
        logger_info(f'BIDS validate fail: {str(e)}')
        raise


def read_result_file() -> str:
    f = open('result.txt', 'r')
    output = f.read()
    return output


def main():
    logger_info('Vault url: ' + os.getenv('VAULT_URL'))
    environment = args.get('environment', 'test')
    logger_info('environment: ' + str(args.get('environment')))
    logger_info('config set: ' + environment)
    try:
        # connect to the postgres database
        db = DBConnection()
        db_session = db.session

        # get arguments
        dataset_id = args['dataset_id']
        refresh_token = args['refresh_token']
        access_token = args['access_token']
        dataset_code = get_dataset_code(dataset_id)

        logger_info(
            'dataset_geid: {}, access_token: {}, \
            refresh_token: {}'.format(
                dataset_id, access_token, refresh_token
            )
        )

        auth_token = {'at': access_token, 'rt': refresh_token}

        locked_node = []
        files_locations = get_files(dataset_code)
        # here add recursive read lock on the dataset
        locked_node, err = lock_nodes(dataset_code)
        if err:
            raise err

        if len(files_locations) == 0:
            send_message(dataset_id, 'failed', 'no files in dataset')
            return
        download_from_minio(files_locations, auth_token)
        logger_info('files are downloaded from minio')

        getProcessOutput()
        result = read_result_file()

        logger_info('BIDS validation result: {}'.format(result))

        bids_output = json.loads(result)

        # remove bids folder after validate
        shutil.rmtree(TEMP_FOLDER)

        current_time = datetime.utcfromtimestamp(time.time())

        logger_info(f'Validation time: {current_time}')

        # Insert the bids output if the database does not store any result before
        # Otherwise update the bids output and updated time
        insert_bids = insert(DatasetModel).values(
            dataset_geid=dataset_id,
            created_time=current_time,
            updated_time=current_time,
            validate_output=json.dumps(bids_output),
        )

        do_update_bids = insert_bids.on_conflict_do_update(
            constraint='dataset_geid',
            set_={DatasetModel.updated_time: current_time, DatasetModel.validate_output: json.dumps(bids_output)},
            where=(DatasetModel.dataset_geid == dataset_id),
        )
        db_session.execute(do_update_bids)
        db_session.commit()

        send_message(dataset_id, 'success', bids_output)

    except Exception as e:
        logger_info(f'BIDs validator failed due to: {str(e)}')
        send_message(dataset_id, 'failed', str(e))
        raise

    finally:
        for resource_key, operation in locked_node:
            unlock_resource(resource_key, operation)


if __name__ == '__main__':
    try:
        args = parse_inputs()
        main()
    except Exception as e:
        logger_info('[Validate Failed] {}'.format(str(e)))
        for info in traceback.format_stack():
            logger_info(info)
        raise
