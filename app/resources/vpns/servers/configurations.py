import json
import sys
from http import HTTPStatus
from typing import List

from flask import Response

from app.service import VPNServerConfigurationAPIService
from rest import APIException, APIResourceURL

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import make_api_response


class VPNServersConfigurationsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'VPNServersConfigurationsAPI'
    __api_url__ = 'vpns/servers/<string:server_suuid>/configurations/user/<string:user_suuid>'

    _config = None

    vpnserversconfigurations_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, VPNServersConfigurationsAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
        ]
        return api_urls

    def __init__(self, vpnserversconfigurations_service: VPNServerConfigurationAPIService, config: dict) -> None:
        super().__init__()
        self.vpnserversconfigurations_service = vpnserversconfigurations_service

        self._config = config

    def post(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, server_suuid: str, user_suuid: str) -> Response:
        try:
            api_response = self.vpnserversconfigurations_service.get_vpnserverconfig(server_uuid=server_suuid,
                                                                                     user_uuid=user_suuid)
            response_data = APIResponse(status=APIResponseStatus.success.value, code=api_response.code,
                                        data=api_response.data, headers=api_response.headers)
            resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
            return resp
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code,
                                        errors=e.errors)
            resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
            return resp
