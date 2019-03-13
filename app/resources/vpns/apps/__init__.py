import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app import RailRoadAPIError

sys.path.insert(1, '../rest_api_library')
from response import make_api_response, make_error_request_response
from api import ResourceAPI, APIResourceURL
from response import APIResponseStatus, APIResponse


class VPNAppsVersionAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'vpns/apps/<string:platform>/version'

    _config = None

    versions = {
        'windows': '1.0a',
        'android': '1.0a',
        'ios': '1.0a'
    }

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{VPNAppsVersionAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST', 'PUT']),
        ]
        return api_urls

    def __init__(self, *args) -> None:
        super().__init__(*args)

    def post(self) -> Response:
        response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.METHOD_NOT_ALLOWED,
                                    error=HTTPStatus.METHOD_NOT_ALLOWED.message,
                                    error_code=HTTPStatus.METHOD_NOT_ALLOWED)

        resp = make_api_response(data=response_data, http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self, sid: int) -> Response:
        response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.METHOD_NOT_ALLOWED,
                                    error=HTTPStatus.METHOD_NOT_ALLOWED.message,
                                    error_code=HTTPStatus.METHOD_NOT_ALLOWED)

        resp = make_api_response(data=response_data, http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, platform: str) -> Response:
        super(VPNAppsVersionAPI, self).get(req=request)

        if platform not in self.versions.keys():
            return make_error_request_response(http_code=HTTPStatus.BAD_REQUEST,
                                               err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        version = self.versions[platform]

        response_data = APIResponse(status=APIResponseStatus.success.status, data={'version': version},
                                    code=HTTPStatus.OK)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
