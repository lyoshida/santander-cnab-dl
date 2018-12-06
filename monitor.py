import json

import requests

from config import MONITOR_API_KEY, MONITOR_URL, MONITOR_GRAPHQL_URL


class HttpClient:
    """
    To read response content: json.loads(repsonse.content)
    """

    @staticmethod
    def get_json(url, params: dict = None, headers: dict = None, jwt: str = '') -> requests.Response:
        """
        Make a get request

        :param url: url
        :param params: dictionary containing query params
        :param headers: dictionary containing headers
        :param jwt: jwt to be passed on the authorization header
        :return: a request Response
        """

        if not headers:
            headers = {}

        if not params:
            params = {}

        headers['Accept'] = 'application/json'

        if jwt:
            headers['Authorization'] = 'Token {}'.format(jwt)

        response = requests.get(url, params=params if params else {}, headers=headers if headers else {})

        return response

    @staticmethod
    def post_json(url, data: dict = None, headers: dict = None, jwt: str = '') -> requests.Response:
        """

        :param url: url
        :param data: dictionary containing the payload
        :param headers: dictionary containing headers
        :param jwt: jwt to be passed on the authorization header
        :return: a request Response
        """

        if not data:
            data = {}

        if not headers:
            headers = {}

        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'

        if jwt:
            headers['Authorization'] = 'Token {}'.format(jwt)

        response = requests.post(url, data=json.dumps(data if data else {}), headers=headers if headers else {})

        return response


class MonitorApi:

    def __init__(self,
                 monitor_url: str = MONITOR_GRAPHQL_URL,
                 monitor_api_key: str = MONITOR_API_KEY):

        self._url = monitor_url
        self._api_key = monitor_api_key

    def create_cnab_file(self, monitor_id: str, content: [str]):
        return HttpClient.post_json(self._url, data={'query': {'monitor_id': monitor_id, 'content': content}})



