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
                 vpnservers_api_service: VPNServersAPIService, *args) -> None:
        super().__init__(*args)
        self._confs_api_service = vpnserversconfigurations_service
        self._vpnservers_api_service = vpnservers_api_service

    def post(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, server_uuid: str, user_uuid: str, suuid: str = None) -> Response:
        super(UsersServersConfigurationsAPI, self).get(req=request)

        platform_id = request.args.get('platform_id', None)
        vpn_type_id = request.args.get('vpn_type_id', None)

        if suuid is None:
            try:
                api_response = self._vpnservers_api_service.get_vpnserver_by_uuid(suuid=server_uuid)
                server = api_response.data

                if platform_id is not None and vpn_type_id is not None:
                    api_response = self._confs_api_service.find_by_platform_and_type(user_uuid=user_uuid,
                                                                                     platform_id=platform_id,
                                                                                     vpn_type_id=vpn_type_id)
                    config_b64_str = api_response.data.get('configuration')

                    config_str = base64.b64decode(config_b64_str).decode("utf-8")
                    config_str = config_str.replace("server_ip", server.get('ip'))
                    config_str = config_str.replace("server_port", server.get('port'))
                    config_b64_str = base64.b64encode(config_str.encode('utf-8'))
                    api_response.data['configuration'] = config_b64_str.decode("utf-8")
                else:
                    api_response = self._confs_api_service.find(user_uuid=user_uuid)

                    for user_config in api_response.data:
                        config_b64_str = user_config.get('configuration')
                        config_str = base64.b64decode(config_b64_str).decode("utf-8")
                        config_str = config_str.replace("server_ip", server.get('ip'))
                        config_str = config_str.replace("server_port", server.get('port'))
                        config_b64_str = base64.b64encode(config_str.encode('utf-8'))
                        user_config['configuration'] = config_b64_str.decode("utf-8")

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
                api_response = self._confs_api_service.get_by_suuid(suuid=suuid, user_uuid=user_uuid)
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
