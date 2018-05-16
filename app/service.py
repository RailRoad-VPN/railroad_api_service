import sys

sys.path.insert(1, '../rest_api_library')
from services.rest import RESTService
from services.response import APIResponse


class UserService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_user(self, user_json: dict) -> APIResponse:
        api_response = self._post(data=user_json, headers=self._headers)
        return api_response

    def update_user(self, user_json: dict):
        url = '%s/uuid/%s' % (self._url, user_json['uuid'])
        api_response = self._put(url=url, data=user_json, headers=self._headers)
        return api_response

    def get_user(self, uuid: str = None, email: str = None) -> APIResponse:
        if uuid:
            url = '%s/uuid/%s' % (self._url, uuid)
        elif email:
            url = '%s/email/%s' % (self._url, email)
        else:
            raise KeyError
        api_response = self._get(url=url)

        return api_response
