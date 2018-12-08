import datetime
import logging
import os
from datetime import date
from os.path import join

import boto3
from config import BUCKET, ACCESS_KEY, SECRET_KEY, DOWNLOAD_FOLDER

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def parse_date(date_str: str) -> date:
    """
    Converts a date string in the format YYYY-MM-DD to a date object
    :param date_str:
    :return:
    """
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def save_to_s3(path: str, filename: str, content: bytes, bucket: str = BUCKET):
    """
    Save file to S3
    :param path:
    :param filename:
    :param content:
    :param bucket:
    :return:
    """

    client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    file = f'{path}/{filename}'
    client.put_object(Bucket=bucket, Key=file, Body=content)
    client.upload_file(f'{DOWNLOAD_FOLDER}/{filename}', bucket, file)


def list_filenames(folder_path: str = '.', extensions: [str] = None) -> [str]:
    """
    Returns a list of filenames in a given path
    :param extensions: a list of extensions ex: ['txt', 'ret']
    :param folder_path: the path to look for files. default is the current folder
    :return: list of filenames found.
    """

    files = [f for f in os.listdir(folder_path) if os.path.isfile(join(folder_path, f))]

    if not extensions:
        return files

    return [f for f in files if f.split('.')[-1] in extensions]


def delete_file(path: str):
    """
    Delete file from tmp directory
    :param path: path inside the download dir
    :return: None
    """

    os.remove(f'{DOWNLOAD_FOLDER}/{path}')
