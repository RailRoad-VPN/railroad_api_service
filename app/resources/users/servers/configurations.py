import base64
import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app import VPNServerTypeEnum, VPNConfigurationPlatform, UserPolicy
from app.exception import RailRoadAPIError
from app.service import UsersVPNServersConfigurationsAPIService, VPNServersAPIService
from utils import check_uuid

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI, APIResourceURL, APIException
from response import APIResponseStatus, APIResponse, make_error_request_response
from response import make_api_response


class UsersServersConfigurationsAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'users/<string:user_id>/servers/<string:server_uuid>/configurations'

    _rrn_vpn_server_configurations_service = None
    _rrn_vpn_servers_api_service = None

    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{UsersServersConfigurationsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET']),
        ]
        return api_urls

    def __init__(self,
                 rrn_vpn_server_configurations_service: UsersVPNServersConfigurationsAPIService,
                 rrn_vpn_servers_api_service: VPNServersAPIService,
                 user_policy: UserPolicy,
                 *args) -> None:
        super().__init__(*args)
        self._rrn_vpn_server_configurations_service = rrn_vpn_server_configurations_service
        self._rrn_vpn_servers_api_service = rrn_vpn_servers_api_service

        self._user_policy = user_policy

    def post(self, user_id: str, server_uuid: str) -> Response:
        super(UsersServersConfigurationsAPI, self).post(req=request)

        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        if user_id.find("@") == -1:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        email = user_id

        config_base64 = request_json.get('config_base64')
        vpn_type = request_json.get('vpn_type')
        platform = request_json.get('platform')

        type_id = VPNServerTypeEnum.find_by_text(text=vpn_type).sid
        platform_id = VPNConfigurationPlatform.find_by_text(text=platform).sid

        user_json = self._user_policy.get_user(email=email).data

        user_uuid = user_json.get('uuid')

        try:
            api_response = self._rrn_vpn_server_configurations_service.create(user_uuid=user_uuid,
                                                                              configuration=config_base64,
                                                                              vpn_device_platform_id=platform_id,
                                                                              vpn_type_id=type_id)
            # conf_uuid = api_response.data['uuid']
            response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code)
            resp = make_api_response(data=response_data, http_code=api_response.code)
            # loc_url = self.__api_url__.replace('<string:user_id>', user_uuid).replace('<string:server_uuid>', 'all') + f"/{conf_uuid}"
            # resp.headers['Location'] = loc_url
            return resp
        except APIException as e:
            self.logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                        errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, server_uuid: str, user_id: str, suuid: str = None) -> Response:
        super(UsersServersConfigurationsAPI, self).get(req=request)

        self.logger.debug("check @ in user_id")
        if user_id.find("@") != -1:
            self.logger.debug("there is @ in user_id. error")
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)
        else:
            self.logger.debug("there is NO @ in user_id. checking user_uuid")
            is_valid = check_uuid(suuid=user_id)
            if not is_valid:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        self.logger.debug("get platform_id and vpn_type_id from request args")
        platform_id = request.args.get('platform_id', None)
        vpn_type_id = request.args.get('vpn_type_id', None)

        if suuid is None:
            try:
                api_response = self._rrn_vpn_servers_api_service.get_vpnserver_by_uuid(suuid=server_uuid)
                server = api_response.data

                if platform_id is not None and vpn_type_id is not None:
                    api_response = self._rrn_vpn_server_configurations_service.find_by_platform_and_type(
                        user_uuid=user_id,
                        platform_id=platform_id,
                        vpn_type_id=vpn_type_id)
                    config_b64_str = api_response.data.get('configuration')

                    config_str = base64.b64decode(config_b64_str).decode("utf-8")
                    config_str = config_str.replace("server_ip", server.get('ip'))
                    config_str = config_str.replace("server_port", server.get('port'))
                    config_b64_str = base64.b64encode(config_str.encode('utf-8'))
                    api_response.data['configuration'] = config_b64_str.decode("utf-8")
                else:
                    api_response = self._rrn_vpn_server_configurations_service.find(user_uuid=user_id)

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
                api_response = self._rrn_vpn_server_configurations_service.get_by_suuid(suuid=suuid, user_uuid=user_id)
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
