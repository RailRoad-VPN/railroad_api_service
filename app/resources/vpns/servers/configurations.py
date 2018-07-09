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
    __api_url__ = 'vpns/servers/<string:server_uuid>/configurations/user/<string:user_uuid>'

    _config = None

    vpnserversconfs_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, VPNServersConfigurationsAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
        ]
        return api_urls

    def __init__(self, vpnserversconfigurations_service: VPNServerConfigurationAPIService, config: dict) -> None:
        super().__init__()
        self.vpnserversconfs_api_service = vpnserversconfigurations_service

        self._config = config

    def post(self) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, server_uuid: str, user_uuid: str) -> Response:
        try:
            api_response = self.vpnserversconfs_api_service.get_vpnserverconfig(server_uuid=server_uuid,
                                                                                user_uuid=user_uuid)
            response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code,
                                        data=api_response.data, headers=api_response.headers)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                        errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp
