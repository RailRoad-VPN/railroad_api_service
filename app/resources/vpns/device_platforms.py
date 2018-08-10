import sys
from http import HTTPStatus
from typing import List

import logging
from flask import Response

from app.exception import RailRoadAPIError
from app.service import VPNDevicePlatformsAPIService
from rest import APIResourceURL, APINotFoundException, APIException

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse, make_error_request_response
from response import make_api_response

logger = logging.getLogger(__name__)


class VPNDevicePlatformsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'VPNDevicePlatformsAPI'
    __api_url__ = 'vpns/device_platforms'

    _config = None

    _vpndeviceplatforms_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{VPNDevicePlatformsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='<int:sid>', methods=['GET']),
        ]
        return api_urls

    def __init__(self, vpndeviceplatforms_api_service: VPNDevicePlatformsAPIService, config: dict) -> None:
        super().__init__()
        self._vpndeviceplatforms_api_service = vpndeviceplatforms_api_service

        self._config = config

    def post(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, sid: int = None) -> Response:
        if sid is not None:
            try:
                sid = int(sid)
            except ValueError:
                return make_error_request_response(HTTPStatus.BAD_REQUEST,
                                                   err=RailRoadAPIError.DEVICEPLATFORM_IDENTITY_ERROR)
            try:
                api_response = self._vpndeviceplatforms_api_service.find_by_id(sid=sid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code,
                                            data=api_response.data, headers=api_response.headers)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APINotFoundException as e:
                logger.error(e)
                http_code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, errors=e.errors)
                return make_api_response(data=response_data, http_code=http_code)
            except APIException as e:
                logger.error(e)
                http_code = HTTPStatus.BAD_REQUEST
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, errors=e.errors)
                return make_api_response(data=response_data, http_code=http_code)
        else:
            try:
                api_response = self._vpndeviceplatforms_api_service.find()
                response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code,
                                            data=api_response.data, headers=api_response.headers)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APINotFoundException as e:
                logger.error(e)
                http_code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, errors=e.errors)
                return make_api_response(data=response_data, http_code=http_code)
            except APIException as e:
                logger.error(e)
                http_code = HTTPStatus.BAD_REQUEST
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, errors=e.errors)
                return make_api_response(data=response_data, http_code=http_code)
