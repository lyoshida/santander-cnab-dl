import json
import logging
import sys
import time
from enum import Enum

import selenium
from config import DOWNLOAD_FOLDER, CHROMEDRIVER_PATH, API_KEY
from helpers import parse_date, save_to_s3, list_filenames, delete_file
from monitor import MonitorApi
from santander import Santander, MainMenu, TransferenciaArquivosMenu


def catch_error(exctype, value, tb):
    logger.exception(tb)
    return response(StatusCode.server_error, ResponseStatus.error, 'Type: {}, Value: {}, Traceback: {}'.format(str(exctype), str(value), str(tb)))


sys.excepthook = catch_error

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ResponseStatus(Enum):
    error = 'error'
    success = 'success'


class StatusCode(Enum):
    ok = 200
    bad_request = 400
    not_authorized = 401
    server_error = 500


def response(status_code: StatusCode, status: ResponseStatus, message: str) -> dict:
    return {
        "isBase64Encoded": False,
        "statusCode": status_code.value,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "Access-Control-Allow-Origin"
        },
        "body": json.dumps({"statusCode": status_code.value, "status": status.value, "message": message})
    }


def download(event, context):
    logger.info('Triggering download handler')

    data = json.loads(event['body'])

    try:
        monitor_id = data['monitor_id']
        agencia = data['agencia'].replace('-', '')
        conta = data['conta'].replace('-', '')
        user = data['user']
        senha = data['senha']
        layout = data['layout']
        cnab_date = data['cnab_date']
        api_key = data['api_key']
    except KeyError:
        return response(StatusCode.bad_request, ResponseStatus.error, 'Body requires keys agencia, conta, user, senha, cnab_date and api_key')

    if api_key != API_KEY:
        return response(StatusCode.not_authorized, ResponseStatus.error, 'Not authorized')

    try:
        logger.info('Instantiating santander class')
        santander = Santander(
            agencia=agencia,
            conta=conta,
            user=user,
            senha=senha,
            cnab_date=cnab_date
        )
        logger.info('Finished instantiating class')
    except selenium.common.exceptions.WebDriverException as e:
        logger.exception(e)
        return response(StatusCode.server_error, ResponseStatus.error, str(e) + ' - ' + CHROMEDRIVER_PATH)
    except Exception as e:
        logger.exception(e)
        return response(StatusCode.server_error, ResponseStatus.error, str(e))

    logger.info('Logging in')
    santander.login()
    time.sleep(2)
    logger.info('Accessing transferencia de arquivos')
    santander.click_main_menu(MainMenu.TRANSFERENCIA_DE_ARQUIVOS)
    time.sleep(2)
    santander.click_transferencia_arquivos_section_link(TransferenciaArquivosMenu.CONSULTAR)
    time.sleep(4)
    santander.click_produto_select("Cobrança")
    santander.click_layout_select(layout)
    santander.click_outros_periodos()

    start_date = parse_date(cnab_date)
    end_date = parse_date(cnab_date)

    santander.set_date_ranges(start_date.strftime('%d%m%Y'), end_date.strftime('%d%m%Y'))
    time.sleep(2)
    logger.info('Getting files')
    santander.get_files()

    time.sleep(10)

    # Read path files and save to S3
    files = list_filenames(folder_path=DOWNLOAD_FOLDER, extensions=['txt', 'TXT'])

    logger.info('files in /tmp')
    logger.info(list_filenames('/tmp'))

    logger.info(f'Files found: {str(files)}')
    for filename in files:
        logger.info(f'Reading {filename}')
        with open(f'{DOWNLOAD_FOLDER}/{filename}') as file:
            file_content = file.read()
            save_to_s3(
                path='033_' + agencia + '_' + conta,
                filename=filename,
                content=file_content
            )

            content = []
            for line in file.readlines():
                content.append(line)
                logger.info('Trying to connect to monitor-api...')
                monitor_response = json.loads(MonitorApi().create_cnab_file(monitor_id, content).content)
                if monitor_response['status'] == 'SUCCESS':
                    logger.info(monitor_response['message'])
                else:
                    logger.error(f'Could not save file on Monitor. {monitor_response["message"]}')

    for filename in files:
        delete_file(filename)

    return response(StatusCode.ok, ResponseStatus.success, 'Saved')
