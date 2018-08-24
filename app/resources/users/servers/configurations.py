import base64
import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.exception import RailRoadAPIError
from app.service import UsersVPNServersConfigurationsAPIService, VPNServersAPIService
from rest import APIException, APIResourceURL
from utils import check_uuid

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse, make_error_request_response
from response import make_api_response


class UsersServersConfigurationsAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'users/<string:user_uuid>/servers/<string:server_uuid>/configurations'

    _config = None

    _confs_api_service = None
    _vpnservers_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{UsersServersConfigurationsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET']),
        ]
        return api_urls

    def __init__(self, vpnserversconfigurations_service: UsersVPNServersConfigurationsAPIService,
                 vpnservers_api_service: VPNServersAPIService, config: dict) -> None:
        super().__init__()
        self._confs_api_service = vpnserversconfigurations_service
        self._vpnservers_api_service = vpnservers_api_service
        self._config = config

    def post(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, server_uuid: str, user_uuid: str, suuid: str = None) -> Response:

        platform_id = request.args.get('platform_id', None)
        vpn_type_id = request.args.get('vpn_type_id', None)

        if suuid is None:
            try:
                api_response = self._confs_api_service.find(server_uuid=server_uuid, user_uuid=user_uuid,
                                                            platform_id=platform_id, vpn_type_id=vpn_type_id)

                config_b64_str = api_response.data.configuration

                api_response = self._vpnservers_api_service.get_vpnserver_by_uuid(suuid=server_uuid)
                server = api_response.data

                config_str = base64.b64decode(config_b64_str)
                config_str.replace("server_ip", server.get('ip'))
                config_str.replace("server_port", server.get('port'))
                config_b64_str = base64.b64encode(config_str)

                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=config_b64_str)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                self.logger.debug(e.serialize())
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
                api_response = self._confs_api_service.get_by_suuid(suuid=suuid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
