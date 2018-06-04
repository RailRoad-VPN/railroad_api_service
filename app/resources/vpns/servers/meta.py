import json
import sys
from http import HTTPStatus
from typing import List

from flask import Response

from app.service import VPNServersMetaAPIService
from rest import APIResourceURL

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import make_api_response


class VPNServersMetaAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'VPNServersMetaAPI'
    __api_url__ = 'vpns/servers/meta'

    _config = None

    vpnserversmeta_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, VPNServersMetaAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
        ]
        return api_urls

    def __init__(self, vpnserversmeta_service: VPNServersMetaAPIService, config: dict) -> None:
        super().__init__()
        self.vpnserversmeta_service = vpnserversmeta_service

        self._config = config

    def post(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        api_response = self.vpnserversmeta_service.get_meta()

        response_data = APIResponse(status=APIResponseStatus.success.value, code=api_response.code,
                                    data=api_response.data, headers=api_response.headers)
        resp = make_api_response(response_data, HTTPStatus.OK)
        return resp
