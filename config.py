import os

LOGIN_URL = 'https://www.santandernetibe.com.br/'
BASE_URL = 'https://pj.santandernetibe.com.br/'
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
BUCKET = os.environ.get('BUCKET')
DOWNLOAD_FOLDER = '/tmp'  # This is the only folder with write permissions inside lambda

API_KEY = os.environ.get('API_KEY')

# AWS
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

# API
MONITOR_URL = os.environ.get('MONITOR_URL')
MONITOR_GRAPHQL_URL = f'{MONITOR_URL}/graphql'
MONITOR_API_KEY = os.environ.get('MONITOR_API_KEY')
