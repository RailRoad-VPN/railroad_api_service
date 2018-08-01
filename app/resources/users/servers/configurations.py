import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response

from app.exception import RailRoadAPIError
from app.service import VPNServerConfigurationAPIService
from rest import APIException, APIResourceURL
from utils import check_uuid

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from response import make_api_response

logger = logging.getLogger(__name__)


class VPNServersConfigurationsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'VPNServersConfigurationsAPI'
    __api_url__ = 'users/<string:user_uuid>/servers/<string:server_uuid>/configuration'

    _config = None

    vpnserversconfs_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{VPNServersConfigurationsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET']),
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

    def get(self, server_uuid: str, user_uuid: str, suuid: str = None) -> Response:
        if suuid is None:
            try:
                api_response = self.vpnserversconfs_api_service.get_vpnserverconfig(server_uuid=server_uuid,
                                                                                    user_uuid=user_uuid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
        else:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=code,
                                            error=RailRoadAPIError.BAD_USER_IDENTITY.message,
                                            error_code=RailRoadAPIError.BAD_USER_IDENTITY)
                resp = make_api_response(data=response_data, http_code=code)
                return resp
            try:
                api_response = self.vpnserversconfs_api_service.get_vpnserverconfig_by_uuid(suuid=suuid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
