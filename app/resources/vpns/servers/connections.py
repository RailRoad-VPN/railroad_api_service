import sys
from http import HTTPStatus
from typing import List

import dateutil.parser
from flask import Response, request

from app.exception import RailRoadAPIError
from app.policy import UserPolicy, logging
from app.service import VPNServerConnectionsAPIService
from utils import check_uuid

sys.path.insert(0, '../rest_api_library')
from rest import APIResourceURL, APIException, APINotFoundException
from api import ResourceAPI
from response import APIResponseStatus, APIResponse, make_error_request_response, check_required_api_fields
from response import make_api_response


class VPNSServersConnectionsAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'vpns/servers/<string:server_uuid>/connections'

    _config = None

    _vpnserverconn_api_service = None
    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{VPNSServersConnectionsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url.replace('/<string:server_uuid>/', '/'), resource_name='', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='', methods=['POST']),
        ]
        return api_urls

    def __init__(self, vpnserverconn_api_service: VPNServerConnectionsAPIService, user_policy: UserPolicy,
                 config: dict) -> None:
        super().__init__()
        self._vpnserverconn_api_service = vpnserverconn_api_service
        self._user_policy = user_policy

        self._config = config

    def post(self, server_uuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        server = request_json.get('server', None)
        server_uuid = server.get('uuid', None)
        server_type = server.get('type', None)
        # TODO think about user count
        users_count = server.get('users_count', None)

        user_list = request_json.get('users', None)

        req_fields = {
            'server': server,
            'type': server_type,
            'users_count': users_count,
            'uuid': server_uuid,
            'users': user_list,
        }

        self.logger.debug(f"{self.__class__}: Check required fields: {req_fields}")

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        if len(user_list) == 0:
            self.logger.debug(f"{self.__class__}: No connections for server.")

            self._vpnserverconn_api_service.disconnect_by_server(server_uuid=server_uuid)

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.NOT_MODIFIED)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        for k, connection_user in user_list.items():
            email = connection_user.get('email')
            bytes_i = connection_user.get('bytes_i')
            bytes_o = connection_user.get('bytes_o')
            connected_since = connection_user.get('connected_since')
            connected_since = dateutil.parser.parse(connected_since)
            device_ip = connection_user.get('device_ip')
            virtual_ip = connection_user.get('virtual_ip')

            api_response = self._user_policy.get_user(email=email)
            user = api_response.data
            user_uuid = user.get('uuid')

            api_response = self._user_policy.get_user_devices(user_uuid=user_uuid)
            user_devices = api_response.data

            user_device = None
            user_device_uuid = None
            NEW_CONNECTION = False
            for ud in user_devices:
                if ud.get('virtual_ip') == virtual_ip:
                    user_device = ud
                    if not user_device.get('is_connected'):
                        NEW_CONNECTION = True
                    user_device['connected_since'] = connected_since
                    user_device['device_ip'] = device_ip
                    user_device['is_connected'] = True
                    user_device['modify_reason'] = 'update connection information'
                    break

            try:
                if user_device is None:
                    user_device_uuid = None
                    self.logger.debug(f"{self.__class__}: We did not found user device for received connection information. "
                                      f"This means it is OpenVPN configuration or something else.")
                    api_response = self._vpnserverconn_api_service.get_current_by_server_and_user_and_vip(
                        server_uuid=server_uuid,
                        virtual_ip=virtual_ip)
                    server_connection = api_response.data
                else:
                    user_device_uuid = user_device.get('uuid')
                    try:
                        self._user_policy.update_user_device(user_device=user_device)
                    except APIException as e:
                        self.logger.error(e)
                        self.logger.error(f"Error while update user device: {user_device}")
                    api_response = self._vpnserverconn_api_service.get_current_by_server_and_user_device(
                        server_uuid=server_uuid,
                        user_device_uuid=user_device_uuid)
                    server_connection = api_response.data

                if NEW_CONNECTION:
                    raise APINotFoundException
                else:
                    self.logger.debug("Update existed connection")
                self.logger.debug(f"{self.__class__}: Got VPN server connection: {server_connection}")

                server_connection['user_device_uuid'] = user_device_uuid
                server_connection['device_ip'] = device_ip
                server_connection['virtual_ip'] = virtual_ip
                server_connection['bytes_i'] = bytes_i
                server_connection['bytes_o'] = bytes_o
                server_connection['connected_since'] = connected_since
                server_connection['is_connected'] = True
                server_connection['modify_reason'] = 'update server connection'
                try:
                    self._vpnserverconn_api_service.update(server_connection_dict=server_connection)
                except APIException as e:
                    self.logger.error("Error while updating vpn server connection")
                    self.logger.error(e)
                    response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                                errors=e.errors)
                    resp = make_api_response(data=response_data, http_code=e.http_code)
                    return resp
            except APINotFoundException:
                self.logger.info("No existed vpn server connection or user device was disconnected")
                try:
                    self._vpnserverconn_api_service.create(server_uuid=server_uuid,
                                                           user_uuid=user_uuid,
                                                           user_device_uuid=user_device_uuid,
                                                           device_ip=device_ip, virtual_ip=virtual_ip,
                                                           bytes_i=bytes_i, bytes_o=bytes_o,
                                                           is_connected=True,
                                                           connected_since=connected_since.isoformat())
                except APIException as e:
                    self.logger.error(e)
                    self.logger.error(f"Error while create server connection")
                    response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                                errors=e.errors)
                    resp = make_api_response(data=response_data, http_code=e.http_code)
                    return resp
            except APIException as e:
                self.logger.debug(e.serialize())
                self.logger.error("Error when getting vpn server connection")
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        super(VPNSServersConnectionsAPI, self).get(req=request)

        user_device_uuid = request.args.get('user_device_uuid', None)
        is_connected = request.args.get('is_connected', None)

        is_valid = check_uuid(user_device_uuid)
        if not is_valid:
            return make_error_request_response(http_code=HTTPStatus.BAD_REQUEST,
                                               err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        try:
            if is_connected:
                api_response = self._vpnserverconn_api_service.get_current_by_user_device(
                    user_device_uuid=user_device_uuid)
            else:
                api_response = self._vpnserverconn_api_service.get_all_by_user_device_uuid(
                    user_device_uuid=user_device_uuid)
            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                        data=api_response.data)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=e.errors)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp
