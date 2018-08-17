import sys
from http import HTTPStatus
from typing import List

from flask import Response

from app.service import VPNServerConnectionsAPIService
from rest import APIResourceURL

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse, make_error_request_response
from response import make_api_response


class VPNSServersConnectionsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = __qualname__
    __api_url__ = 'vpns/servers/meta'

    _config = None

    vpnserversmeta_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{VPNSServersConnectionsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
        ]
        return api_urls

    def __init__(self, vpnserversmeta_service: VPNServerConnectionsAPIService, config: dict) -> None:
        super().__init__()
        self.vpnserversmeta_api_service = vpnserversmeta_service

        self._config = config

    def post(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        api_response = self.vpnserversmeta_api_service.get_meta()

        response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code,
                                    data=api_response.data, headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
